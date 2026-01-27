from typing import List,Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
from .base_agent import BaseAgent
from core.agent_config import AgentConfig, AgentType
from core.research_state import ResearchState
from core.advanced_research import AdvancedResearch
from core.content_analyzer import ContentAnalyzer
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage



class ResearchCoordinatorAgent(BaseAgent):
    """Orchestrates the research process"""
    def __init__(self):
        config = AgentConfig(
            agent_type=AgentType.RESEARCH_COORDINATOR,
            system_prompt="""You are a Research Coordinator. Your responsibilities:
            1. Analyze the research topic and break it into subtopics
            2. Determine the appropriate research methodology
            3. Coordinate between different specialist agents
            4. Monitor research progress and quality
            5. Synthesize final findings

            You must ensure comprehensive coverage and academic rigor."""
        )
        super().__init__(config)

    async def coordinate(self, state: ResearchState) -> Dict[str, Any]:
        """Coordinate the research process"""
        self.log_activity("coordination_started", {"topic": state["topic"].dict()})


        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.config.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""
            Research Topic: {state['topic'].title}
            Domain: {state['topic'].domain}
            Complexity: {state['topic'].complexity}

            Create a comprehensive research plan including:
            1. Key research questions
            2. Required data sources
            3. Methodology outline
            4. Success criteria
            5. Timeline estimate
            """)
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({
            "messages": state.get("messages", [])
        })


        coordination_result = {
            "research_plan": response.content,
            "next_phase": "literature_review",
            "assigned_agents": [
                AgentType.SEARCH_SPECIALIST.value,
                AgentType.ANALYST.value
            ],
            "timestamp": datetime.now().isoformat()
        }

        self.log_activity("coordination_completed", coordination_result)

        return {"research_phase": "literature_review", "analysis": coordination_result}
