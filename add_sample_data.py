#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SECRET_KEY', 'your-secret-key')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emojimind.settings')

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django
django.setup()

from game.models import GameWord

def add_sample_words():
    # Easy words
    easy_words = [
        'Computer', 'Phone', 'Car', 'Tree', 'House', 'Dog', 'Cat', 'Sun', 'Moon', 'Water',
        'Fire', 'Book', 'Music', 'Love', 'Happy', 'Food', 'Coffee', 'Pizza', 'Heart', 'Star'
    ]
    
    # Medium words  
    medium_words = [
        'Birthday', 'Christmas', 'Vacation', 'School', 'Hospital', 'Restaurant', 'Airport', 
        'Shopping', 'Wedding', 'Party', 'Movie', 'Football', 'Basketball', 'Swimming', 
        'Dancing', 'Cooking', 'Fishing', 'Camping', 'Exercise', 'Reading'
    ]
    
    # Hard words
    hard_words = [
        'Earthquake', 'Democracy', 'Philosophy', 'Cryptocurrency', 'Artificial Intelligence',
        'Global Warming', 'Time Travel', 'Social Media', 'Video Conference', 'Online Learning',
        'Space Exploration', 'Renewable Energy', 'Virtual Reality', 'Machine Learning', 
        'Quantum Physics', 'Blockchain', 'Biotechnology', 'Nanotechnology', 'Cybersecurity', 'Automation'
    ]
    
    # Add easy words
    for word in easy_words:
        obj, created = GameWord.objects.get_or_create(
            word=word,
            difficulty='easy'
        )
        if created:
            print(f"Added easy word: {word}")
    
    # Add medium words
    for word in medium_words:
        obj, created = GameWord.objects.get_or_create(
            word=word,
            difficulty='medium'
        )
        if created:
            print(f"Added medium word: {word}")
    
    # Add hard words
    for word in hard_words:
        obj, created = GameWord.objects.get_or_create(
            word=word,
            difficulty='hard'
        )
        if created:
            print(f"Added hard word: {word}")
    
    print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_words()
