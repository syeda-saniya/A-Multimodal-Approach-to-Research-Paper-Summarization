from abc import ABC, abstractmethod
import os
import logging
from datetime import datetime
import json
from typing import Dict

class BaseProcessor(ABC):
    """Abstract base class for PDF processors."""
    
    def __init__(self, output_base_dir: str = "pdf_output"):
        self.output_base_dir = output_base_dir
        self._setup_logging()
        self._setup_directories()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def _setup_directories(self):
        """Create necessary directories for output."""
        pass
    
    def _create_directory(self, path: str):
        """Safely create directory if it doesn't exist."""
        os.makedirs(path, exist_ok=True)
        
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _save_json(self, data: Dict, filepath: str):
        """Save dictionary data as JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)