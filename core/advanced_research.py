from typing import List, Dict
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import ArxivAPIWrapper
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib


class AdvancedResearch:
  def __init__(self):
    self.search_tool = DuckDuckGoSearchRun()
    self.arxiv_wrapper = ArxivAPIWrapper()
    self.cache = {}

  def search_with_cache(self,query:str,max_results:int=5) -> Dict[str,any]:
    cache_key = hashlib.md5(query.encode()).hexdigest() # Corrected from m5 to md5
    if cache_key in self.cache:
      return self.cache[cache_key]

    try:
      with ThreadPoolExecutor(max_workers=3) as executor: # Corrected typo: ThreadPoolEcecutor -> ThreadPoolExecutor
        futures=[
            executor.submit(self._web_search,query,max_results),
            executor.submit(self._arxiv_search,query,max_results),
            executor.submit(self._scholar_search,query,max_results),
        ]
        results=[]
        for future in as_completed(futures):
          try:
            results.extend(future.result())
          except Exception as e:
            print(f"Search error {e}")
      unique_results = self._deduplicate_results(results)
      result_dict={
          "query":query,
          "timestamp":datetime.now().isoformat(),
          "results":unique_results[:max_results]
      }
      self.cache[cache_key]=result_dict
      return result_dict
    except Exception as e: # Added missing except block
      print(f"An error occurred in search_with_cache: {e}")
      return {
          "query": query,
          "timestamp": datetime.now().isoformat(),
          "results": [],
          "error": str(e)
      }

  def _web_search(self,query:str,max_results:int) -> List[Dict]:
    try:
      results = self.search_tool.run(query)
      return [{
          "source":"web",
          "content":results[:1000],
          "relevance_score":0.8
      }]
    except:
      return []

  def _arxiv_search(self, query: str, max_results: int) -> List[Dict]:
        """Search arXiv for academic papers"""
        try:
            docs = self.arxiv_wrapper.load(query[:300])
            return [{
                "source": "arxiv",
                "title": doc.metadata.get("Title", ""),
                "authors": doc.metadata.get("Authors", []),
                "summary": doc.page_content[:500],
                "published": doc.metadata.get("Published", ""),
                "relevance_score": 0.9
            } for doc in docs[:max_results]]
        except:
            return []

  def _scholar_search(self, query: str, max_results: int) -> List[Dict]: # Corrected indentation
        """Mock scholar search (replace with actual API)"""
        return [{
            "source": "scholar",
            "title": f"Research on {query}",
            "abstract": f"This paper discusses {query} in detail...",
            "citations": 42,
            "relevance_score": 0.85
        }]

  def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
    seen = set()
    unique=[]
    for result in results:
      content_hash = hashlib.md5(str(result.get('title','') + result.get('content', '')).encode()).hexdigest()
      if content_hash not in seen:
        seen.add(content_hash)
        unique.append(result) # Corrected: append result, not hash
    return unique