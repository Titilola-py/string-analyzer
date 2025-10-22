from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import os

from database import engine, get_db, Base
from models import AnalyzedString
from schemas import StringInput, StringResponse, StringListResponse, NaturalLanguageResponse
from analyzer import analyze_string
from nlp_parser import parse_natural_language_query, validate_parsed_filters

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="String Analyzer Service",
    description="API for analyzing and storing string properties",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "String Analyzer Service API",
        "version": "1.0.0",
        "endpoints": {
            "POST /strings": "Analyze and store a new string",
            "GET /strings/{string_value}": "Get a specific string's analysis",
            "GET /strings": "Get all strings with optional filtering",
            "GET /strings/filter-by-natural-language": "Filter using natural language",
            "DELETE /strings/{string_value}": "Delete a string"
        }
    }


@app.post("/strings", response_model=StringResponse, status_code=201)
async def create_string(string_input: StringInput, db: Session = Depends(get_db)):
    """
    Analyze and store a new string.
    
    Returns 201 if successful, 409 if string already exists, 400/422 for invalid input.
    """
    try:
        value = string_input.value
        
        # Check if string already exists
        existing = db.query(AnalyzedString).filter(AnalyzedString.value == value).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="String already exists in the system"
            )
        
        properties = analyze_string(value)
        
        db_string = AnalyzedString(
            id=properties["sha256_hash"],
            value=value,
            length=properties["length"],
            is_palindrome=properties["is_palindrome"],
            unique_characters=properties["unique_characters"],
            word_count=properties["word_count"],
            sha256_hash=properties["sha256_hash"],
            character_frequency_map=properties["character_frequency_map"]
        )
        
        db.add(db_string)
        db.commit()
        db.refresh(db_string)
        
        return db_string.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/strings/{string_value}", response_model=StringResponse)
async def get_string(string_value: str, db: Session = Depends(get_db)):
    """
    Get a specific string's analysis.
    
    Returns 200 if found, 404 if not found.
    """
    db_string = db.query(AnalyzedString).filter(AnalyzedString.value == string_value).first()
    
    if not db_string:
        raise HTTPException(
            status_code=404,
            detail="String does not exist in the system"
        )
    
    return db_string.to_dict()


@app.get("/strings", response_model=StringListResponse)
async def get_all_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None, ge=0),
    max_length: Optional[int] = Query(None, ge=0),
    word_count: Optional[int] = Query(None, ge=0),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
    db: Session = Depends(get_db)
):
    """
    Get all strings with optional filtering.
    
    Query parameters:
    - is_palindrome: Filter by palindrome status
    - min_length: Minimum string length
    - max_length: Maximum string length
    - word_count: Exact word count
    - contains_character: Single character to search for
    """
    try:
        query = db.query(AnalyzedString)
        
        filters_applied = {}
        
        if is_palindrome is not None:
            query = query.filter(AnalyzedString.is_palindrome == is_palindrome)
            filters_applied["is_palindrome"] = is_palindrome
        
        if min_length is not None:
            query = query.filter(AnalyzedString.length >= min_length)
            filters_applied["min_length"] = min_length
        
        if max_length is not None:
            query = query.filter(AnalyzedString.length <= max_length)
            filters_applied["max_length"] = max_length
        
        if word_count is not None:
            query = query.filter(AnalyzedString.word_count == word_count)
            filters_applied["word_count"] = word_count
        
        if contains_character is not None:
            all_strings = query.all()
            filtered_strings = [s for s in all_strings if contains_character in s.value]
            filters_applied["contains_character"] = contains_character
            
            return {
                "data": [s.to_dict() for s in filtered_strings],
                "count": len(filtered_strings),
                "filters_applied": filters_applied
            }
        
        results = query.all()
        
        return {
            "data": [s.to_dict() for s in results],
            "count": len(results),
            "filters_applied": filters_applied if filters_applied else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid query parameters: {str(e)}")


@app.get("/strings/filter-by-natural-language", response_model=NaturalLanguageResponse)
async def filter_by_natural_language(
    query: str = Query(..., description="Natural language query"),
    db: Session = Depends(get_db)
):
    """
    Filter strings using natural language queries.
    
    Examples:
    - "all single word palindromic strings"
    - "strings longer than 10 characters"
    - "strings containing the letter z"
    """
    try:
        # Parse the natural language query
        parsed_filters = parse_natural_language_query(query)
        
        if not parsed_filters:
            raise HTTPException(
                status_code=400,
                detail="Unable to parse natural language query"
            )
        
        validation_error = validate_parsed_filters(parsed_filters)
        if validation_error:
            raise HTTPException(
                status_code=422,
                detail=f"Query parsed but resulted in conflicting filters: {validation_error}"
            )
        
        db_query = db.query(AnalyzedString)
        
        if "is_palindrome" in parsed_filters:
            db_query = db_query.filter(AnalyzedString.is_palindrome == parsed_filters["is_palindrome"])
        
        if "min_length" in parsed_filters:
            db_query = db_query.filter(AnalyzedString.length >= parsed_filters["min_length"])
        
        if "max_length" in parsed_filters:
            db_query = db_query.filter(AnalyzedString.length <= parsed_filters["max_length"])
        
        if "word_count" in parsed_filters:
            db_query = db_query.filter(AnalyzedString.word_count == parsed_filters["word_count"])
        
        results = db_query.all()
        
        # Filter by character if needed
        if "contains_character" in parsed_filters:
            char = parsed_filters["contains_character"]
            results = [s for s in results if char in s.value]
        
        return {
            "data": [s.to_dict() for s in results],
            "count": len(results),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed_filters
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to parse natural language query: {str(e)}")


@app.delete("/strings/{string_value}", status_code=204)
async def delete_string(string_value: str, db: Session = Depends(get_db)):
    """
    Delete a string from the system.
    
    Returns 204 if successful, 404 if not found.
    """
    db_string = db.query(AnalyzedString).filter(AnalyzedString.value == string_value).first()
    
    if not db_string:
        raise HTTPException(
            status_code=404,
            detail="String does not exist in the system"
        )
    
    db.delete(db_string)
    db.commit()
    
    return None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "string-analyzer"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)