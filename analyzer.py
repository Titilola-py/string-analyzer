import hashlib
from typing import Dict

def analyze_string(value: str) -> Dict:
    """
    Analyze a string and compute all required properties.
    
    Args:
        value: The string to analyze
        
    Returns:
        Dictionary containing all computed properties
    """
    # 1. Length
    length = len(value)
    
    # 2. Is Palindrome (case-insensitive, ignoring spaces)
    cleaned = value.replace(" ", "").lower()
    is_palindrome = cleaned == cleaned[::-1]
    
    # 3. Unique Characters
    unique_characters = len(set(value))
    
    # 4. Word Count (split by whitespace)
    word_count = len(value.split())
    
    # 5. SHA-256 Hash
    sha256_hash = hashlib.sha256(value.encode()).hexdigest()
    
    # 6. Character Frequency Map
    character_frequency_map = {}
    for char in value:
        character_frequency_map[char] = character_frequency_map.get(char, 0) + 1
    
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map
    }