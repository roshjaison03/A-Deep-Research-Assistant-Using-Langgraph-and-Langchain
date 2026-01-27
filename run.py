from graph.research_assistant_graph import ResearchAssistantGraph
from data_display import display_research_improved
from core.research_topic import ResearchTopic


async def run_and_display():
    topic = ResearchTopic(
        title="Discounted Cash Flow in modern world",
        domain="Finance",
        complexity="expert"
    )
    
    assistant = ResearchAssistantGraph()
    result = await assistant.run_research(topic)
    
    display_research_improved(result)
    
    return result

# Execute
import asyncio
result = asyncio.run(run_and_display())