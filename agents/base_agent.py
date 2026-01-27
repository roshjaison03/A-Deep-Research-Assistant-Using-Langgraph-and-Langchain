from typing import Dict
import logging
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from core.agent_config import AgentConfig
from dotenv import load_dotenv
import os

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

class BaseAgent:
  def __init__(self,config = AgentConfig):
    self.config = config
    self.llm = self.initiate_llm()
    self.tools = config.tools
    self.logger = self._setup_logger()

  def initiate_llm(self):   
        return ChatOpenAI(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model="liquid/lfm-2.5-1.2b-instruct:free",
        )

  def _setup_logger(self):
        """Setup agent-specific logger"""
        logger = logging.getLogger(self.config.agent_type.value)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f"logs/{self.config.agent_type.value}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

  def log_activity(self, activity: str, metadata: Dict = None):
        """Log agent activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.config.agent_type.value,
            "activity": activity,
            "metadata": metadata or {}
        }
        self.logger.info(json.dumps(log_entry))
        return log_entry