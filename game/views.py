# Home view for landing page and game over logic
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import EmojiForm
from .models import GameSession, GameWord, UserGameProgress
import random
import google.generativeai as genai
from django.conf import settings
from datetime import datetime, timedelta
import pytz
import re

EMOJI_LIMITS = {"easy": 4, "medium": 4, "hard": 3}
AI_GUESS_LIMIT = {"easy": 2, "medium": 5, "hard": 10}

# Gemini setup
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_or_create_user_progress(user):
    """Get or create user progress tracking"""
    progress, created = UserGameProgress.objects.get_or_create(user=user)
    return progress

@login_required
def home(request):
    # Get user's progress
    progress = get_or_create_user_progress(request.user)
    
    # Check if user has expired or completed the game
    if progress.game_expired:
        return render(request, "game/home.html", {"game_over": True, "reason": "time_expired"})
    
    if progress.game_completed:
        if progress.game_won:
            return render(request, "game/home.html", {"game_over": True, "reason": "won_all"})
        else:
            return render(request, "game/home.html", {"game_over": True, "reason": "lost_game"})
    
    # Remove timer/session if user finished or is starting fresh
    request.session.pop('start_time', None)
    
    # Pass progress info to template
    context = {
        "easy_completed": progress.easy_completed,
        "medium_completed": progress.medium_completed,
        "hard_completed": progress.hard_completed,
        "easy_won": progress.easy_won,
        "medium_won": progress.medium_won,
        "hard_won": progress.hard_won,
    }
    return render(request, "game/home.html", context)

def get_word(difficulty):
    words = list(GameWord.objects.filter(difficulty=difficulty))
    if not words:
        return None
    return random.choice(words).word


def ai_guess_emojis_gemini(emojis, difficulty):
    # Use Gemini API to get AI guesses based on emojis and difficulty
    prompt = (
        "You are an AI for an emoji guessing game. "
        "The user will provide only emojis as input (no text, no numbers, no punctuation, only emojis). "
        f"Your task is to guess the most likely English word or phrase that the emojis represent, based on the given difficulty: {difficulty}. "
        "If difficulty is easy, return top 2 words. If difficulty is medium, return top 5 words. If difficulty is hard, return top 10 words. "
        "Return your guesses as a simple list, one word per line. Do not use quotation marks, brackets, or any special formatting. "
        "Do not explain your reasoning, do not include any text except the words. "
        f"Example format:\nMouse\nRodent\nRat\n\nEmojis: {emojis}"
    )
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    
    # Clean and parse guesses from response
    guesses = []
    if hasattr(response, 'text') and response.text:
        # Split by newlines and clean each guess
        raw_guesses = response.text.strip().split('\n')
        for guess in raw_guesses:
            # Clean the guess: remove quotes, brackets, extra whitespace
            clean_guess = guess.strip().strip('"').strip("'").strip('[]').strip()
            if clean_guess and not clean_guess.startswith('Example') and len(clean_guess) > 0:
                guesses.append(clean_guess)
        
        # If no newlines, try splitting by commas
        if len(guesses) <= 1 and ',' in response.text:
            guesses = []
            raw_guesses = response.text.strip().split(',')
            for guess in raw_guesses:
                clean_guess = guess.strip().strip('"').strip("'").strip('[]').strip()
                if clean_guess and not clean_guess.startswith('Example') and len(clean_guess) > 0:
                    guesses.append(clean_guess)
    
    # Fallback if nothing parsed
    if not guesses and hasattr(response, 'text'):
        guesses = [response.text.strip().strip('"').strip("'")]
    
    # Limit guesses to AI_GUESS_LIMIT and remove empty strings
    valid_guesses = [g for g in guesses if g.strip()][:AI_GUESS_LIMIT[difficulty]]
    
    return valid_guesses

@login_required
def play(request, difficulty):
    # Get user's progress
    progress = get_or_create_user_progress(request.user)
    
    # Block user if they have expired or completed the entire game
    if progress.game_expired or progress.game_completed:
        return redirect('home')
        
    # Check if this difficulty is already completed
    difficulty_completed = getattr(progress, f"{difficulty}_completed", False)
    if difficulty_completed:
        return redirect('home')  # Redirect if already completed this difficulty
    
    emoji_limit = EMOJI_LIMITS[difficulty]
    tries = request.session.get(f"{difficulty}_tries", 0)
    
    # Start timer only if it's the user's first time playing (new user)
    timer = request.session.get('start_time')
    if not timer and not progress.game_started:
        # This is a new user - start the timer
        progress.game_started = True
        progress.game_start_time = timezone.now()
        progress.save()
        request.session['start_time'] = timezone.now().isoformat()
        timer = request.session['start_time']
    elif not timer and progress.game_started:
        # User has played before, restore timer
        if progress.game_start_time:
            request.session['start_time'] = progress.game_start_time.isoformat()
            timer = request.session['start_time']
    
    # --- Timer check: if timer expired, mark as expired ---
    if timer and progress.game_start_time:
        try:
            start_time = progress.game_start_time
            if timezone.now() > (start_time + timedelta(minutes=10)):
                progress.game_expired = True
                progress.game_end_time = start_time + timedelta(minutes=10)
                progress.total_time_taken = timedelta(minutes=10)
                progress.save()
                return redirect('home')
        except Exception:
            pass
    
    # Check if user has already completed this difficulty and redirect to home
    difficulty_completed = getattr(progress, f"{difficulty}_completed", False)
    if difficulty_completed:
        return redirect('home')
    
    error_message = None
    if request.method == "POST":
        form = EmojiForm(request.POST)
        word = request.session.get('game_word')
        if not word:
            return redirect('home')
        if form.is_valid():
            emojis = form.cleaned_data["emojis"]
            # Check emoji limit
            if len(emojis) > emoji_limit * 2:
                form.add_error("emojis", f"Use up to {emoji_limit} emojis.")
            else:
                ai_guesses = ai_guess_emojis_gemini(emojis, difficulty)
                win = word.lower() in [g.lower() for g in ai_guesses]
                
                # Save session timing
                start_time = progress.game_start_time if progress.game_start_time else timezone.now()
                now = timezone.now()
                time_taken = now - start_time
                finished = win and (now <= start_time + timedelta(minutes=10))
                expired = False
                # If timer expired, mark as expired
                if now > start_time + timedelta(minutes=10):
                    expired = True
                    progress.game_expired = True
                    progress.game_end_time = start_time + timedelta(minutes=10)
                    progress.total_time_taken = timedelta(minutes=10)
                    progress.save()
                
                GameSession.objects.create(
                    user=request.user,
                    difficulty=difficulty,
                    word=word,
                    emoji_input=emojis,
                    ai_guesses=ai_guesses,
                    player_win=win,
                    start_time=start_time,
                    end_time=now,
                    time_taken=time_taken if finished else timedelta(minutes=10),
                    finished=finished,
                    expired=expired,
                )
                
                # Update progress when user wins OR when they complete 3 tries
                tries_after = tries + 1
                if win or tries_after >= 3:
                    # Mark this difficulty as completed
                    setattr(progress, f"{difficulty}_completed", True)
                    setattr(progress, f"{difficulty}_won", win)
                    
                    # Check if all difficulties are completed
                    if progress.easy_completed and progress.medium_completed and progress.hard_completed:
                        progress.game_completed = True
                        progress.game_end_time = timezone.now()
                        if progress.easy_won and progress.medium_won and progress.hard_won:
                            progress.game_won = True
                    
                    progress.save()
                
                request.session[f"{difficulty}_tries"] = tries_after
                request.session[f"{difficulty}_win"] = win
                return redirect("result", difficulty)
    else:
        # New round: pick a word and store it in session
        word = get_word(difficulty)
        if not word:
            return render(request, "game/no_words.html", {"difficulty": difficulty})
        request.session['game_word'] = word
        form = EmojiForm()
    
    tries_left = 3 - tries
    context = {
        "difficulty": difficulty,
        "word": request.session.get('game_word'),
        "form": form,
        "emoji_limit": emoji_limit,
        "tries": tries,
        "tries_left": tries_left,
        "error_message": error_message,
        "timer": timer,
    }
    return render(request, "game/play.html", context)

@login_required
def result(request, difficulty):
    progress = get_or_create_user_progress(request.user)
    win = request.session.get(f"{difficulty}_win", False)
    tries = request.session.get(f"{difficulty}_tries", 1)
    
    # Get the latest game session for this user and difficulty
    last_session = GameSession.objects.filter(
        user=request.user,
        difficulty=difficulty
    ).order_by('-id').first()
    ai_guesses = last_session.ai_guesses if last_session else []

    # --- Timer: End game and store time ---
    if last_session and not last_session.finished and progress.game_start_time:
        now = timezone.now()
        start_time = progress.game_start_time
        # Calculate if user finished in time
        if now <= start_time + timedelta(minutes=10):
            # User finished in time
            last_session.end_time = now
            last_session.time_taken = now - start_time
            last_session.finished = True
            last_session.expired = False
        else:
            # User did not finish in time
            last_session.end_time = start_time + timedelta(minutes=10)
            last_session.time_taken = timedelta(minutes=10)
            last_session.finished = False
            last_session.expired = True
            # Update progress
            progress.game_expired = True
            progress.game_end_time = last_session.end_time
            progress.total_time_taken = last_session.time_taken
            progress.save()
        last_session.save()

    # Pass timer for JS display
    timer = request.session.get('start_time')
    
    # Check if this difficulty round is complete (3 tries used or won)
    difficulty_complete = tries >= 3 or win
    
    # Show continue options based on game state
    show_try_again = tries < 3 and not win and not progress.game_expired
    show_next_difficulty = difficulty_complete and not progress.game_expired and not progress.game_completed
    
    context = {
        "difficulty": difficulty,
        "win": win,
        "tries": tries,
        "ai_guesses": ai_guesses,
        "word": last_session.word if last_session else None,
        "emojis": last_session.emoji_input if last_session else None,
        "time_taken": last_session.time_taken if last_session else None,
        "finished": last_session.finished if last_session else False,
        "expired": progress.game_expired,
        "show_try_again": show_try_again,
        "show_next_difficulty": show_next_difficulty,
        "difficulty_complete": difficulty_complete,
        "timer": timer,
    }
    return render(request, "game/result.html", context)