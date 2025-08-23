from django.contrib import admin
from .models import GameWord, GameSession, UserGameProgress

@admin.register(UserGameProgress)
class UserGameProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_email', 'game_started', 'game_completed', 'game_won', 
        'total_time_taken', 'easy_won', 'medium_won', 'hard_won', 'game_expired',
        'game_start_time', 'game_end_time'
    )
    list_filter = ('game_completed', 'game_won', 'game_expired', 'easy_won', 'medium_won', 'hard_won')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_email', 'difficulty', 'player_win', 'finished',
        'time_taken', 'start_time', 'end_time', 'tries', 'solved_words', 'total_words', 'expired', 'score'
    )
    list_filter = ('difficulty', 'player_win', 'finished', 'expired')
    search_fields = ('user__username', 'user__email', 'word')
    readonly_fields = ('user', 'difficulty', 'word')
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(GameWord)