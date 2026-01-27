from pydantic import BaseModel, Field, validator
from typing import List

class ResearchTopic(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    domain: str = Field(..., description="e.g., 'AI', 'Physics', 'Biology'")
    complexity: str = Field("intermediate", pattern="^(beginner|intermediate|advanced|expert)$")
    subtopics: List[str] = Field(default_factory=list)

    @validator('title')
    def title_must_be_meaningful(cls, v):
        if len(v.split()) < 2:
            raise ValueError("Title must be at least 2 words")
        return v