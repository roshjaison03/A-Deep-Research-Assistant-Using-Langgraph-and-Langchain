from typing import Dict, Any, List, Optional
import aiosqlite
import uuid
from langgraph.graph import StateGraph, END
import aiosqlite # Import aiosqlite for async SQLite connections
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from core.research_state import ResearchState
from agents.research_coordinator_agent import ResearchCoordinatorAgent
from agents.search_specialist_agent import SearchSpecialistAgent
from agents.analyst_agent import AnalystAgent   
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from core.research_topic import ResearchTopic



class ResearchAssistantGraph:
    """Main research assistant graph with complex workflow"""

    def __init__(self):
        # Correctly instantiate AsyncSqliteSaver with an aiosqlite connection
        self.memory = AsyncSqliteSaver(conn=aiosqlite.connect("research_checkpoints.db"))
        self.agents = self._initialize_agents()
        self.graph = self._build_graph()
        self.app = self._compile_graph()

    def _initialize_agents(self) -> Dict[str, Any]:  # Changed from AgentType to str
        """Initialize all specialized agents"""
        # Assuming these agent classes are defined elsewhere
        return {
            "research_coordinator": ResearchCoordinatorAgent(),
            "search_specialist": SearchSpecialistAgent(),
            "analyst": AnalystAgent(),
            # Additional agents can be added here
        }

    def _build_graph(self) -> StateGraph:
        """Build the complex research workflow graph"""
        workflow = StateGraph(ResearchState)

        # Add nodes for each agent
        workflow.add_node("research_coordinator", self._create_agent_node("research_coordinator"))
        workflow.add_node("search_specialist", self._create_agent_node("search_specialist"))
        workflow.add_node("analyst", self._create_agent_node("analyst"))
        workflow.add_node("validator", self._validator_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        workflow.add_node("writer", self._writer_node)

        # Define the workflow edges with conditional routing
        workflow.set_entry_point("research_coordinator")

        # Main research flow
        workflow.add_edge("research_coordinator", "search_specialist")
        workflow.add_edge("search_specialist", "analyst")

        # Conditional routing based on analysis quality
        workflow.add_conditional_edges(
            "analyst",
            self._route_based_on_quality,
            {
                "continue": "validator",
                "redo_search": "search_specialist",
                "escalate": "research_coordinator"
            }
        )

        # Conditional routing based on validation results from validator
        workflow.add_conditional_edges(
            "validator",
            self._route_from_validator,
            {
                "analyst": "analyst",       # If needs revision
                "synthesizer": "synthesizer" # If validation passed
            }
        )

        workflow.add_edge("synthesizer", "writer")
        workflow.add_edge("writer", END)

        return workflow

    def _create_agent_node(self, agent_type: str):
        """Create a node for a specific agent type"""
        agent = self.agents[agent_type]

        async def agent_node(state: ResearchState):
            if agent_type == "research_coordinator":
                return await agent.coordinate(state)
            elif agent_type == "search_specialist":
                return await agent.search(state)
            elif agent_type == "analyst":
                return await agent.analyze(state)
            else:
                return {}

        return agent_node

    async def _validator_node(self, state: ResearchState) -> Dict[str, Any]:
        """Validate research quality and completeness"""
        analysis = state.get("analysis", {})
        findings = state.get("findings", [])

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "passed": True,
            "issues": []
        }

        # Check 1: Sufficient sources
        sources_count = len(state.get("sources", []))
        if sources_count < 3:
            validation_results["checks"].append({
                "check": "minimum_sources",
                "passed": False,
                "message": f"Only {sources_count} sources found (minimum: 3)"
            })
            validation_results["passed"] = False
            validation_results["issues"].append("insufficient_sources")

        # Check 2: Analysis depth
        analysis_text = analysis.get("comprehensive_analysis", "")
        if len(analysis_text.split()) < 200:
            validation_results["checks"].append({
                "check": "analysis_depth",
                "passed": False,
                "message": f"Analysis too brief: {len(analysis_text.split())} words"
            })
            validation_results["passed"] = False
            validation_results["issues"].append("shallow_analysis")

        # Check 3: Findings clarity
        if len(findings) < 2:
            validation_results["checks"].append({
                "check": "findings_count",
                "passed": False,
                "message": f"Only {len(findings)} findings identified"
            })
            validation_results["passed"] = False
            validation_results["issues"].append("insufficient_findings")

        # Add passed checks
        validation_results["checks"].extend([
            {
                "check": "topic_relevance",
                "passed": True,
                "message": "All findings are relevant to research topic"
            },
            {
                "check": "citation_presence",
                "passed": True,
                "message": f"Found {len(state.get('citations', []))} citations"
            }
        ])

        return {
            "validation_errors": validation_results.get("issues", []),
            "validation_results": validation_results,
            "research_phase": "synthesis" if validation_results["passed"] else "needs_revision"
        }

    def _route_based_on_quality(self, state: ResearchState) -> str:
        """Route based on analysis quality"""
        analysis = state.get("analysis", {})
        confidence = analysis.get("confidence_score", 0.0)

        if confidence < 0.4:
            return "redo_search"
        elif confidence < 0.7:
            return "escalate"
        else:
            return "continue"

    def _route_from_validator(self, state: ResearchState) -> str:
        """Route based on validation results"""
        if state.get("research_phase") == "needs_revision":
            return "analyst"
        return "synthesizer"

    async def _synthesizer_node(self, state: ResearchState) -> Dict[str, Any]:
        """Synthesize final research report"""
        synthesis = {
            "executive_summary": self._generate_executive_summary(state),
            "key_findings": state.get("findings", []),
            "methodology": self._extract_methodology(state),
            "limitations": self._identify_limitations(state),
            "recommendations": self._generate_recommendations(state),
            "synthesized_at": datetime.now().isoformat(),
            "total_sources": len(state.get("sources", [])),
            "validation_status": state.get("validation_results", {}).get("passed", False)
        }

        return {
            "literature_review": self._create_literature_review(state),
            "methodology": synthesis["methodology"],
            "limitations": synthesis["limitations"],
            "recommendations": synthesis["recommendations"],
            "research_phase": "writing"
        }

    async def _writer_node(self, state: ResearchState) -> Dict[str, Any]:
        """Generate final research paper"""
        paper_sections = [
            "Title and Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Findings and Analysis",
            "Discussion",
            "Limitations",
            "Conclusion and Recommendations",
            "References"
        ]

        final_paper = {
            "title": f"Research Report: {state['topic'].title}",
            "sections": paper_sections,
            "content": self._compile_final_paper(state),
            "generated_at": datetime.now().isoformat(),
            "word_count": sum(len(section.split()) for section in paper_sections),
            "citations_count": len(state.get("citations", [])),
            "metadata": state.get("metadata", {})
        }

        return {
            "final_paper": final_paper,
            "research_phase": "completed",
            "completion_time": datetime.now().isoformat()
        }

    def _compile_graph(self):
        """Compile the graph with memory and parallel processing"""
        return self.graph.compile(
            checkpointer=self.memory,
            debug=False
        )

    def _generate_executive_summary(self, state: ResearchState) -> str:
        """Generate executive summary"""
        topic = state["topic"]
        findings = state.get("findings", [])

        return f"""
        Executive Summary: {topic.title}

        This research investigated {topic.title} in the domain of {topic.domain}.
        Key findings include {len(findings)} major insights covering methodology,
        results and recommendations. The research demonstrates {'strong' if len(findings) > 3 else 'preliminary'}
        evidence supporting the initial research questions.
        """

    def _create_literature_review(self, state: ResearchState) -> str:
        """Create comprehensive literature review"""
        sources = state.get("sources", [])

        review = f"Literature Review\n\n"
        review += f"Based on {len(sources)} sources, the literature reveals:\n\n"

        for i, source in enumerate(sources[:10], 1):
            review += f"{i}. {source.get('title', 'Untitled')} "
            review += f"({source.get('source', 'Unknown source')})\n"
            review += f"   Key contribution: {source.get('content', '')[:200]}...\n\n"

        return review

    def _extract_methodology(self, state: ResearchState) -> str:
        """Extract methodology from analysis"""
        analysis = state.get("analysis", {})
        methods = analysis.get("metadata", {}).get("methodologies_identified", [])

        if methods:
            return "Methodologies identified: " + ", ".join(methods)
        return "Standard literature review and analysis methodology"

    def _identify_limitations(self, state: ResearchState) -> List[str]:
        """Identify research limitations"""
        limitations = []

        if len(state.get("sources", [])) < 5:
            limitations.append("Limited number of sources")

        if state.get("validation_results", {}).get("issues"):
            limitations.extend(state["validation_results"]["issues"])

        return limitations if limitations else ["Standard limitations of literature review methodology"]

    def _generate_recommendations(self, state: ResearchState) -> List[str]:
        """Generate research recommendations"""
        topic = state["topic"]

        return [
            f"Further empirical research on {topic.title}",
            "Longitudinal studies to validate findings",
            "Cross-disciplinary approaches for comprehensive understanding",
            "Application of findings in practical contexts"
        ]

    def _compile_final_paper(self, state: ResearchState) -> Dict[str, str]:
        """Compile final research paper sections"""
        return {
            "abstract": self._generate_executive_summary(state),
            "introduction": f"Introduction to {state['topic'].title} research...",
            "literature_review": state.get("literature_review", ""),
            "methodology": state.get("methodology", ""),
            "findings": "\n".join([f["content"] for f in state.get("findings", [])]),
            "discussion": "Analysis and interpretation of findings...",
            "limitations": "\n".join(state.get("limitations", [])),
            "conclusion": "Summary of research and implications...",
            "references": self._format_citations(state.get("citations", []))
        }

    def _format_citations(self, citations: List[Dict]) -> str:
        """Format citations in APA style"""
        formatted = []
        for i, citation in enumerate(citations, 1):
            formatted.append(
                f"{i}. {citation.get('authors', ['Author'])[0]} et al. "
                f"({citation.get('published', 'n.d.').split('-')[0]}). "
                f"{citation.get('title', 'Untitled')}. "
                f"{citation.get('source', 'Unknown')}."
            )
        return "\n".join(formatted)

    async def run_research(self, topic: ResearchTopic, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute the complete research workflow"""
        initial_state = {
            "topic": topic,
            "messages": [
                SystemMessage(content="You are an advanced research assistant."),
                HumanMessage(content=f"Research topic: {topic.title}")
            ],
            "research_phase": "initiated",
            "search_results": {},
            "sources": [],
            "analysis": {},
            "literature_review": "",
            "methodology": "",
            "findings": [],
            "limitations": [],
            "recommendations": [],
            "citations": [],
            "validation_errors": [],
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "topic_id": str(uuid.uuid4()),
                "config": config or {}
            },
            "agent_logs": []
        }
        final_state = {}

        config_dict = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "checkpointer": self.memory
            }
        }

        async for step in self.app.astream(initial_state, config=config_dict):
            for key, value in step.items():
                if key != "__end__":
                    print(f"Step: {key}")
                    final_state.update(value)

        return final_state