from typing import TypedDict
from typing import Any, List, Dict
from typing_extensions import Annotated
from core.research_topic import ResearchTopic
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    topic: ResearchTopic
    research_phase: str
    search_results: Dict[str, Any]
    sources: List[Dict[str, str]]
    analysis: Dict[str, Any]
    literature_review: str
    methodology: str
    findings: List[Dict[str, Any]]
    limitations: List[str]
    recommendations: List[str]
    citations: List[Dict[str, str]]
    validation_errors: List[str]
    metadata: Dict[str, Any]
    agent_logs: List[Dict[str, Any]]
