from typing import Dict
# from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ContentAnalyzer:
  def __init__(self):
    self.Embeddings = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap=200
    )
  def analyze_content(self,content) -> Dict[str,any]:
    chunks = self.text_splitter.split_text(content)
    embeddings = self.Embeddings.encode(chunks)
    word_count = len(content.split())
    sent_count =len(content.split('.'))
    return {
        "chunks": len(chunks),
            "word_count": word_count,
            "sentence_count": sent_count
    }