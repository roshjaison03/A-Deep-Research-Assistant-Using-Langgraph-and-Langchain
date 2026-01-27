from typing import Dict, Any
import asyncio
from datetime import datetime
import uuid
from .base_agent import BaseAgent
from core.agent_config import AgentConfig, AgentType
from core.research_state import ResearchState
from core.advanced_research import AdvancedResearch
from core.content_analyzer import ContentAnalyzer

class SearchSpecialistAgent(BaseAgent):
    """Specializes in finding and evaluating sources"""
    def __init__(self):
        config = AgentConfig(
            agent_type=AgentType.SEARCH_SPECIALIST,
            system_prompt="""You are a Search Specialist. Your responsibilities:
            1. Find relevant academic and web sources
            2. Evaluate source credibility and relevance
            3. Extract key information from sources
            4. Maintain source citations
            5. Identify knowledge gaps

            Prioritize recent, authoritative sources."""
        )
        super().__init__(config)
        self.search_tool = AdvancedResearch()
        self.content_analyzer = ContentAnalyzer()

    async def search(self, state: ResearchState) -> Dict[str, Any]:
        """Perform comprehensive search"""
        topic = state["topic"]


        queries = [
            f"{topic.title} recent developments",
            f"{topic.domain} {topic.title} research papers",
            f"{topic.title} methodology best practices"
        ]

 
        search_tasks = [self._execute_search(query) for query in queries]
        search_results = await asyncio.gather(*search_tasks)


        processed_results = []
        citations = []

        for result_batch in search_results:
            for result in result_batch.get("results", []):

                if "content" in result or "summary" in result:
                    content = result.get("content", result.get("summary", ""))
                    analysis = self.content_analyzer.analyze_content(content)

                    processed_result = {
                        **result,
                        "analysis": analysis,
                        "processed_at": datetime.now().isoformat()
                    }
                    processed_results.append(processed_result)

  
                    citation = {
                        "id": str(uuid.uuid4()),
                        "title": result.get("title", "Untitled"),
                        "authors": result.get("authors", ["Unknown"]),
                        "source": result.get("source", "Unknown"),
                        "url": result.get("url", ""),
                        "accessed_at": datetime.now().isoformat()
                    }
                    citations.append(citation)

        self.log_activity("search_completed", {
            "queries": queries,
            "results_found": len(processed_results),
            "citations_generated": len(citations)
        })

        return {
            "search_results": processed_results,
            "sources": processed_results,
            "citations": citations,
            "research_phase": "analysis"
        }

    async def _execute_search(self, query: str) -> Dict[str, Any]:
        """Execute a single search query"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.search_tool.search_with_cache, query, 3
        )