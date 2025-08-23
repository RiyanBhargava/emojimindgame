from django.db import models
from django.contrib.auth.models import User

class GameWord(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    word = models.CharField(max_length=100, unique=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return f"{self.word} ({self.difficulty})"

class UserGameProgress(models.Model):
    """Track overall game progress for each user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_started = models.BooleanField(default=False)
    game_start_time = models.DateTimeField(null=True, blank=True)
    game_end_time = models.DateTimeField(null=True, blank=True)
    total_time_taken = models.DurationField(null=True, blank=True)
    
    # Track completion status for each difficulty
    easy_completed = models.BooleanField(default=False)
    medium_completed = models.BooleanField(default=False) 
    hard_completed = models.BooleanField(default=False)
    
    # Track wins for each difficulty
    easy_won = models.BooleanField(default=False)
    medium_won = models.BooleanField(default=False)
    hard_won = models.BooleanField(default=False)
    
    # Overall game status
    game_completed = models.BooleanField(default=False)  # All 3 difficulties attempted
    game_won = models.BooleanField(default=False)  # Won all 3 difficulties
    game_expired = models.BooleanField(default=False)  # Timer expired
    
    def __str__(self):
        return f"{self.user.username} - Progress"

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The player
    difficulty = models.CharField(max_length=10)              # easy/medium/hard
    word = models.CharField(max_length=100)                   # The answer word for this round
    emoji_input = models.CharField(max_length=100)            # User's emoji input
    ai_guesses = models.JSONField()                           # AI's guesses (list)
    player_win = models.BooleanField()                        # Did player win this round?
    start_time = models.DateTimeField(null=True, blank=True)  # When the game started
    end_time = models.DateTimeField(null=True, blank=True)    # When the game ended/finished
    time_taken = models.DurationField(null=True, blank=True)  # How much time was taken
    finished = models.BooleanField(default=False)             # Did the user finish all words in time?
    tries = models.IntegerField(default=0)                    # How many tries for this word
    total_words = models.IntegerField(default=0)              # Total words to solve in this game
    solved_words = models.IntegerField(default=0)             # How many words user solved
    expired = models.BooleanField(default=False)              # Did the timer expire?
    score = models.IntegerField(default=0)                    # (Optional) Calculated score

    def __str__(self):
        return f"{self.user.username} - {self.difficulty} - {self.start_time}"