from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from datetime import datetime

class StringInput(BaseModel):
    """Schema for creating a new string"""
    value: str = Field(..., description="String to analyze")
    
    @validator('value')
    def value_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('value cannot be empty')
        return v

class StringProperties(BaseModel):
    """String analysis properties"""
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]

class StringResponse(BaseModel):
    """Response schema for a single string"""
    id: str
    value: str
    properties: StringProperties
    created_at: str

class StringListResponse(BaseModel):
    """Response schema for list of strings"""
    data: List[StringResponse]
    count: int
    filters_applied: Optional[Dict] = None

class NaturalLanguageResponse(BaseModel):
    """Response for natural language queries"""
    data: List[StringResponse]
    count: int
    interpreted_query: Dict