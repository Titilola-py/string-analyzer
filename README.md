# String Analyzer Service - Stage 1

A RESTful API service that analyzes strings and stores their computed properties with advanced filtering capabilities including natural language queries.

## Features

- String analysis (length, palindrome, character frequency, etc.)
- SHA-256 hashing for unique identification
- Persistent storage with SQLite
- Advanced filtering with query parameters
- Natural language query support
- Full CRUD operations
- Automatic API documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Language**: Python 3.8+
- **Server**: Uvicorn

## API Endpoints

### 1. Create/Analyze String

**POST** `/strings`

Analyzes a string and stores its properties.

**Request:**
```json
{
  "value": "racecar"
}
```

**Response (201 Created):**
```json
{
  "id": "abc123...",
  "value": "racecar",
  "properties": {
    "length": 7,
    "is_palindrome": true,
    "unique_characters": 4,
    "word_count": 1,
    "sha256_hash": "abc123...",
    "character_frequency_map": {
      "r": 2,
      "a": 2,
      "c": 2,
      "e": 1
    }
  },
  "created_at": "2025-10-17T20:00:00Z"
}
```

**Error Responses:**
- `409 Conflict` - String already exists
- `400 Bad Request` - Invalid request body
- `422 Unprocessable Entity` - Invalid data type

### 2. Get Specific String

**GET** `/strings/{string_value}`

Retrieves analysis for a specific string.

**Response (200 OK):**
```json
{
  "id": "abc123...",
  "value": "racecar",
  "properties": { ... },
  "created_at": "2025-10-17T20:00:00Z"
}
```

**Error Response:**
- `404 Not Found` - String doesn't exist

### 3. Get All Strings with Filtering

**GET** `/strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a`

Retrieves all strings with optional filters.

**Query Parameters:**
- `is_palindrome` (boolean) - Filter by palindrome status
- `min_length` (integer) - Minimum string length
- `max_length` (integer) - Maximum string length
- `word_count` (integer) - Exact word count
- `contains_character` (string) - Single character to search for

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "hash1",
      "value": "string1",
      "properties": { ... },
      "created_at": "2025-10-17T20:00:00Z"
    }
  ],
  "count": 15,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5
  }
}
```

### 4. Natural Language Filtering

**GET** `/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`

Filter strings using natural language queries.

**Supported Query Examples:**
- "all single word palindromic strings"
- "strings longer than 10 characters"
- "strings containing the letter z"
- "palindromic strings that contain the first vowel"

**Response (200 OK):**
```json
{
  "data": [ ... ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
```

**Error Responses:**
- `400 Bad Request` - Unable to parse query
- `422 Unprocessable Entity` - Conflicting filters

### 5. Delete String

**DELETE** `/strings/{string_value}`

Deletes a string from the system.

**Response:**
- `204 No Content` - Success (empty body)

**Error Response:**
- `404 Not Found` - String doesn't exist

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd string-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work fine)
   ```

5. **Run the application**
   ```bash
   python main.py
   ```
   
   Or use uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## Testing the API

### Using curl

**Create a string:**
```bash
curl -X POST http://localhost:8000/strings \
  -H "Content-Type: application/json" \
  -d '{"value": "racecar"}'
```

**Get a string:**
```bash
curl http://localhost:8000/strings/racecar
```

**Filter strings:**
```bash
curl "http://localhost:8000/strings?is_palindrome=true&word_count=1"
```

**Natural language query:**
```bash
curl "http://localhost:8000/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings"
```

**Delete a string:**
```bash
curl -X DELETE http://localhost:8000/strings/racecar
```

### Using FastAPI Docs

1. Navigate to http://localhost:8000/docs
2. Try out endpoints interactively
3. View request/response schemas

## String Analysis Properties

For each analyzed string, the service computes:

1. **length** - Total number of characters
2. **is_palindrome** - Reads same forwards/backwards (case-insensitive)
3. **unique_characters** - Count of distinct characters
4. **word_count** - Number of words (split by whitespace)
5. **sha256_hash** - Unique cryptographic hash
6. **character_frequency_map** - Count of each character

## Natural Language Parser

The NLP parser