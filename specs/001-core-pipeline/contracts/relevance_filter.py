# Contract: NFL Relevance Filter

**Purpose**: Define interface for filtering articles for NFL relevance

## Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from enum import Enum

class FilterDecision(Enum):
    KEEP = "keep"
    REJECT = "reject"
    ESCALATE = "escalate"  # Send to LLM

class RelevanceFilter(ABC):
    @abstractmethod
    def filter_article(self, article: Dict[str, Any]) -> Tuple[FilterDecision, float]:
        """Apply filtering rules to determine NFL relevance"""
        pass

    @abstractmethod
    def is_nfl_team_mention(self, text: str) -> bool:
        """Check if text mentions NFL teams"""
        pass

    @abstractmethod
    def is_nfl_url_pattern(self, url: str) -> bool:
        """Check if URL matches NFL patterns"""
        pass
```

## Data Contracts

### Input: Article
```json
{
  "url": "https://example.com/article",
  "title": "Chiefs Sign New Quarterback",
  "publisher": "NFL.com",
  "publication_date": "2025-09-06T10:00:00Z"
}
```

### Output: Filter Result
- Decision: FilterDecision enum
- Score: float (0.0 to 1.0)

## Filtering Rules

### Include Rules (High Priority)
- URL contains: /nfl/, /chiefs/, /patriots/, etc.
- Title contains: NFL team names, player names
- Publisher is known NFL source

### Exclude Rules (High Priority)
- URL contains: /nba/, /mlb/, /soccer/, /nhl/
- Title contains: non-NFL sports terms
- Publisher is non-sports or other league

### Escalate to LLM
- Ambiguous titles without clear team/player mentions
- Mixed content that might be NFL-related

## Performance Requirements
- Rule evaluation: <1ms per article
- Memory efficient: Pre-compile regex patterns
- Thread-safe: No shared mutable state
