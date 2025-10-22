import re
from typing import Dict, Optional

def parse_natural_language_query(query: str) -> Dict:
    """
    Parse a natural language query into filter parameters.
    
    Supports queries like:
    - "all single word palindromic strings"
    - "strings longer than 10 characters"
    - "strings containing the letter z"
    - "palindromic strings that contain the first vowel"
    
    Args:
        query: Natural language query string
        
    Returns:
        Dictionary of parsed filters
    """
    query_lower = query.lower()
    filters = {}
    
    # Parse word count
    # "single word" → word_count=1
    if "single word" in query_lower or "one word" in query_lower:
        filters["word_count"] = 1
    elif "two word" in query_lower or "2 word" in query_lower:
        filters["word_count"] = 2
    elif "three word" in query_lower or "3 word" in query_lower:
        filters["word_count"] = 3
    
    # Parse palindrome
    if "palindrom" in query_lower:
        filters["is_palindrome"] = True
    
    # Parse length constraints
    # "longer than X" → min_length=X+1
    longer_than = re.search(r'longer than (\d+)', query_lower)
    if longer_than:
        filters["min_length"] = int(longer_than.group(1)) + 1
    
    # "shorter than X" → max_length=X-1
    shorter_than = re.search(r'shorter than (\d+)', query_lower)
    if shorter_than:
        filters["max_length"] = int(shorter_than.group(1)) - 1
    
    # "at least X characters" → min_length=X
    at_least = re.search(r'at least (\d+)', query_lower)
    if at_least:
        filters["min_length"] = int(at_least.group(1))
    
    # "at most X characters" → max_length=X
    at_most = re.search(r'at most (\d+)', query_lower)
    if at_most:
        filters["max_length"] = int(at_most.group(1))
    
    # Parse character containment
    # "containing the letter X" or "contain X"
    letter_match = re.search(r'contain(?:ing)?(?: the)?(?: letter)? ([a-z])', query_lower)
    if letter_match:
        filters["contains_character"] = letter_match.group(1)
    
    # "first vowel" → 'a'
    if "first vowel" in query_lower:
        filters["contains_character"] = "a"
    
    # "last vowel" → 'u'
    if "last vowel" in query_lower:
        filters["contains_character"] = "u"
    
    return filters


def validate_parsed_filters(filters: Dict) -> Optional[str]:
    """
    Validate that parsed filters don't conflict.
    
    Args:
        filters: Dictionary of filters
        
    Returns:
        Error message if conflicting, None if valid
    """
    if "min_length" in filters and "max_length" in filters:
        if filters["min_length"] > filters["max_length"]:
            return "Conflicting length constraints: min_length cannot be greater than max_length"
    
    return None