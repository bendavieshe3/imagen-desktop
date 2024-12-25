"""Handles saving and managing generation outputs."""
import requests
from pathlib import Path
from typing import List
from ..utils.debug_logger import logger

class OutputManager:
    """Handles saving and managing generation outputs."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure the cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_outputs(self, prediction_id: str, output_urls: List[str]) -> List[Path]:
        """
        Save generation outputs to local cache.
        Returns list of saved file paths.
        """
        prediction_dir = self.cache_dir / prediction_id
        prediction_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        
        for i, url in enumerate(output_urls):
            # Skip if the input looks like a local path
            if not url.startswith(('http://', 'https://')):
                logger.warning(f"Skipping non-URL input: {url}")
                continue
                
            file_path = prediction_dir / f"output_{i}.png"
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                    
                saved_paths.append(file_path)
                logger.debug(f"Saved output {i} for prediction {prediction_id}")
                
            except Exception as e:
                logger.error(f"Failed to save output {i} from {url}: {str(e)}")
                continue
        
        return saved_paths
    
    def get_prediction_outputs(self, prediction_id: str) -> List[Path]:
        """Get list of saved output files for a prediction."""
        prediction_dir = self.cache_dir / prediction_id
        if prediction_dir.exists():
            return sorted(prediction_dir.glob("output_*.png"))
        return []
    
    def cleanup_outputs(self, prediction_id: str) -> int:
        """
        Remove output files for a prediction.
        Returns number of files removed.
        """
        prediction_dir = self.cache_dir / prediction_id
        if not prediction_dir.exists():
            return 0
        
        count = 0
        for file_path in prediction_dir.glob("output_*.png"):
            try:
                file_path.unlink()
                count += 1
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {str(e)}")
        
        try:
            prediction_dir.rmdir()  # Remove directory if empty
        except Exception:
            pass  # Ignore if directory not empty
        
        return count