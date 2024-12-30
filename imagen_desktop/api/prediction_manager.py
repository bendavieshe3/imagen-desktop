"""Manages prediction lifecycle and polling."""
import threading
import time
from typing import Any, List
from PyQt6.QtCore import QObject, pyqtSignal
from ..utils.debug_logger import logger
from .client import ReplicateClient

class PredictionManager(QObject):
    """Manages prediction lifecycle and polling."""
    
    # Signals
    generation_started = pyqtSignal(str)  # prediction_id
    generation_progress = pyqtSignal(str, int)  # prediction_id, progress
    generation_completed = pyqtSignal(str, list)  # prediction_id, output_urls
    generation_failed = pyqtSignal(str, str)  # prediction_id, error_message
    generation_canceled = pyqtSignal(str)  # prediction_id
    
    def __init__(self, client: ReplicateClient):
        super().__init__()
        self.client = client
        self._active_predictions = {}  # Store active prediction threads
    
    def _normalize_output(self, output: Any) -> List[str]:
        """Normalize prediction output to a list of URLs."""
        if output is None:
            return []
        elif isinstance(output, str):
            return [output]
        elif isinstance(output, list):
            return output
        else:
            return [str(output)]
    
    def _poll_prediction(self, prediction_id: str):
        """Poll prediction status until completion."""
        try:
            while prediction_id in self._active_predictions:
                try:
                    prediction = self.client.get_prediction(prediction_id)
                    
                    if prediction.status == 'succeeded':
                        if prediction.output is not None:
                            normalized_output = self._normalize_output(prediction.output)
                            self.generation_completed.emit(prediction_id, normalized_output)
                        break
                    elif prediction.status == 'failed':
                        self.generation_failed.emit(prediction_id, prediction.error or "Unknown error")
                        break
                    elif prediction.status == 'canceled':
                        self.generation_canceled.emit(prediction_id)
                        break
                    
                    # Wait before next poll
                    time.sleep(1)
                    
                except Exception as e:
                    self.generation_failed.emit(prediction_id, str(e))
                    break
        finally:
            # Always clean up
            if prediction_id in self._active_predictions:
                del self._active_predictions[prediction_id]
    
    def start_prediction(self, model_identifier: str, params: dict) -> str:
        """
        Start a new prediction.
        Returns the prediction ID.
        """
        try:
            prediction = self.client.create_prediction(model_identifier, **params)
            
            # Store thread for cancellation
            thread = threading.Thread(
                target=self._poll_prediction,
                args=(prediction.id,),
                daemon=True
            )
            self._active_predictions[prediction.id] = {
                'thread': thread,
                'prediction': prediction
            }
            
            # Start polling
            thread.start()
            self.generation_started.emit(prediction.id)
            
            return prediction.id
            
        except Exception as e:
            error_msg = f"Failed to start prediction: {str(e)}"
            logger.error(error_msg)
            self.generation_failed.emit("", error_msg)
            raise
    
    def cancel_prediction(self, prediction_id: str):
        """Cancel an active prediction."""
        if prediction_id in self._active_predictions:
            try:
                self.client.cancel_prediction(prediction_id)
                del self._active_predictions[prediction_id]
                self.generation_canceled.emit(prediction_id)
                
            except Exception as e:
                error_msg = f"Failed to cancel prediction: {str(e)}"
                logger.error(error_msg)
                self.generation_failed.emit(prediction_id, error_msg)