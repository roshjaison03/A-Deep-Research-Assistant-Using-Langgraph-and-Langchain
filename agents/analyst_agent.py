from typing import Dict, Any,List
import json
from datetime import datetime
import uuid
from .base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from core.agent_config import AgentConfig
from core.agent_type import AgentType
from core.research_state import ResearchState

class AnalystAgent(BaseAgent):
    """Analyzes and synthesizes information"""
    def __init__(self):
        config = AgentConfig(
            agent_type=AgentType.ANALYST,
            system_prompt="""You are an Analysis Specialist. Your responsibilities:
            1. Analyze collected data and sources
            2. Identify patterns, trends, and relationships
            3. Evaluate evidence quality and bias
            4. Generate insights and hypotheses
            5. Create structured analysis reports

            Maintain objectivity and academic rigor."""
        )
        super().__init__(config)

    async def analyze(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze search results and generate insights"""
        search_results = state.get("search_results", [])
        topic = state["topic"]


        analysis_data = {
            "topic": topic.dict(),
            "sources_count": len(search_results),
            "sources_by_type": {},
            "key_findings": [],
            "methodologies_identified": [],
            "knowledge_gaps": []
        }

        for result in search_results:
            source_type = result.get("source", "unknown")
            analysis_data["sources_by_type"][source_type] = \
                analysis_data["sources_by_type"].get(source_type, 0) + 1

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.config.system_prompt),
            HumanMessage(content=f"""
            Analyze these research findings for topic: {topic.title}

            Search Results Summary:
            {json.dumps(search_results[:5], indent=2)}

            Provide a comprehensive analysis covering:
            1. Key trends and patterns
            2. Conflicting viewpoints
            3. Research methodologies used
            4. Evidence strength assessment
            5. Identified knowledge gaps
            6. Preliminary conclusions
            """)
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({})

   
        analysis_result = {
            "comprehensive_analysis": response.content,
            "metadata": analysis_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "confidence_score": self._calculate_confidence(search_results)
        }

        self.log_activity("analysis_completed", {
            "topic": topic.title,
            "sources_analyzed": len(search_results),
            "confidence": analysis_result["confidence_score"]
        })

        return {
            "analysis": analysis_result,
            "research_phase": "synthesis",
            "findings": self._extract_findings(response.content)
        }

    def _calculate_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence score based on source quality"""
        if not results:
            return 0.0

        scores = []
        for result in results:
       
            base_score = result.get("relevance_score", 0.5)
            source_bonus = {
                "arxiv": 0.3,
                "scholar": 0.3,
                "web": 0.1
            }.get(result.get("source", ""), 0.0)
            scores.append(min(1.0, base_score + source_bonus))

        return sum(scores) / len(scores) if scores else 0.0

    def _extract_findings(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract structured findings from analysis"""
        findings = []
        lines = analysis.split('\n')

        for line in lines:
            if any(keyword in line.lower() for keyword in ['finding', 'conclusion', 'result', 'shows']):
                findings.append({
                    "id": str(uuid.uuid4()),
                    "content": line.strip(),
                    "category": self._categorize_finding(line),
                    "confidence": 0.8
                })

        return findings

    def _categorize_finding(self, finding: str) -> str:
        """Categorize finding type"""
        finding_lower = finding.lower()
        if any(word in finding_lower for word in ['method', 'approach', 'technique']):
            return "methodology"
        elif any(word in finding_lower for word in ['result', 'finding', 'shows', 'indicates']):
            return "result"
        elif any(word in finding_lower for word in ['limitation', 'gap', 'challenge']):
            return "limitation"
        elif any(word in finding_lower for word in ['recommend', 'suggest', 'propose']):
            return "recommendation"
        return "observation"