from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from datetime import datetime, timezone
from database import Base

class AnalyzedString(Base):
    __tablename__ = "analyzed_strings"
    
    id = Column(String, primary_key=True, index=True)

    value = Column(String, nullable=False, unique=True, index=True)

    length = Column(Integer, nullable=False)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=False)
    character_frequency_map = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        """Convert model to dictionary for API response"""
        return {
            "id": self.id,
            "value": self.value,
            "properties": {
                "length": self.length,
                "is_palindrome": self.is_palindrome,
                "unique_characters": self.unique_characters,
                "word_count": self.word_count,
                "sha256_hash": self.sha256_hash,
                "character_frequency_map": self.character_frequency_map
            },
            "created_at": self.created_at.isoformat()
        }