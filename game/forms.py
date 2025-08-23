
from django import forms
from allauth.account.forms import SignupForm
import emoji
import re

class DisabledSignupForm(SignupForm):
    """Custom signup form that redirects to Google OAuth"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear all fields to prevent manual signup
        self.fields.clear()

class EmojiForm(forms.Form):
    emojis = forms.CharField(
        max_length=20,
        help_text='Enter emojis only.',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 💻☁️📡'})
    )

    def clean_emojis(self):
        data = self.cleaned_data['emojis']
        # Remove whitespace for validation
        data_no_space = data.replace(' ', '')
        
        if not data_no_space:
            raise forms.ValidationError('Please enter emoji only.')
        
        # Method 1: Use emoji library to detect ALL emojis
        # This will detect every single emoji in the Unicode standard
        emoji_data = emoji.emoji_list(data_no_space)
        extracted_emojis = ''.join([item['emoji'] for item in emoji_data])
        
        # Check if the input consists ONLY of emojis
        if extracted_emojis == data_no_space:
            return data_no_space
        
        # Method 2: If emoji library fails, use comprehensive Unicode ranges
        # This covers ALL emoji Unicode blocks
        emoji_pattern = re.compile(
            r'^['
            # Emoticons (deprecated but still used)
            r'\u2194-\u2199\u21a9-\u21aa'
            # Miscellaneous Symbols
            r'\u231a-\u231b\u2328\u23cf\u23e9-\u23f3\u23f8-\u23fa'
            r'\u24c2\u25aa-\u25ab\u25b6\u25c0\u25fb-\u25fe'
            r'\u2600-\u27ff'  # Miscellaneous Symbols and Dingbats
            # Supplemental Symbols and Pictographs  
            r'\U0001f000-\U0001f02f'  # Mahjong Tiles
            r'\U0001f030-\U0001f093'  # Domino Tiles
            r'\U0001f0a0-\U0001f0f5'  # Playing Cards
            # Miscellaneous Symbols and Pictographs
            r'\U0001f100-\U0001f1ff'  # Enclosed Alphanumeric Supplement
            r'\U0001f200-\U0001f2ff'  # Enclosed Ideographic Supplement
            r'\U0001f300-\U0001f5ff'  # Miscellaneous Symbols and Pictographs
            # Emoticons
            r'\U0001f600-\U0001f64f'  # Emoticons
            # Transport and Map Symbols
            r'\U0001f680-\U0001f6ff'  # Transport and Map Symbols
            # Alchemical Symbols
            r'\U0001f700-\U0001f77f'  # Alchemical Symbols
            # Geometric Shapes Extended
            r'\U0001f780-\U0001f7ff'  # Geometric Shapes Extended
            # Supplemental Arrows-C
            r'\U0001f800-\U0001f8ff'  # Supplemental Arrows-C
            # Supplemental Symbols and Pictographs
            r'\U0001f900-\U0001f9ff'  # Supplemental Symbols and Pictographs
            # Chess Symbols
            r'\U0001fa00-\U0001fa6f'  # Chess Symbols
            # Symbols and Pictographs Extended-A
            r'\U0001fa70-\U0001faff'  # Symbols and Pictographs Extended-A
            # CJK Symbols and Punctuation (some emoji-like characters)
            r'\u3030\u303d'
            # Enclosed CJK Letters and Months (some emoji-like characters)
            r'\u3297\u3299'
            # Additional symbols that might be used as emojis
            r'\u00a9\u00ae'  # Copyright, Registered
            r'\u203c\u2049'  # Double exclamation, exclamation question
            r'\u2122\u2139'  # Trade mark, Information
            r'\u2194-\u2199'  # Arrows
            r'\u21a9-\u21aa'  # Arrows
            r'\u231a-\u231b'  # Watch
            r'\u2328'  # Keyboard
            r'\u2388'  # Helm
            r'\u23cf'  # Eject
            r'\u23e9-\u23f3'  # Media controls
            r'\u23f8-\u23fa'  # Media controls
            r'\u24c2'  # M
            r'\u25aa-\u25ab'  # Squares
            r'\u25b6'  # Play
            r'\u25c0'  # Reverse
            r'\u25fb-\u25fe'  # Squares
            # Modifier symbols
            r'\U0001f3fb-\U0001f3ff'  # Skin tone modifiers
            # Zero Width Joiner for complex emojis
            r'\u200d'
            # Variation selectors
            r'\ufe0f\ufe0e'
            r']+$'
        )
        
        if emoji_pattern.match(data_no_space):
            return data_no_space
        
        # If both methods fail, it's not all emojis
        raise forms.ValidationError('Please enter emoji only.')