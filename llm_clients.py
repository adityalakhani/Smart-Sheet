"""
LLM Client management for Google Gemini models
Handles both Pro and Flash Lite clients with rate limiting and error handling
"""

import time
import logging
from typing import Dict, Any, Optional
from google import genai
from config import Config
import threading
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple rate limiter for API calls
    """
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests (int): Maximum requests allowed in time window
            time_window (int): Time window in seconds (default: 60 seconds)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without exceeding rate limit
        
        Returns:
            bool: True if request can be made
        """
        with self.lock:
            now = datetime.now()
            # Remove old requests outside time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < timedelta(seconds=self.time_window)]
            
            return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a new request"""
        with self.lock:
            self.requests.append(datetime.now())
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        while not self.can_make_request():
            time.sleep(1)
        self.record_request()

class GeminiClient:
    """
    Wrapper for Google Gemini client with enhanced error handling and logging
    """
    
    def __init__(self, model_name: str, rate_limiter: RateLimiter):
        """
        Initialize Gemini client
        
        Args:
            model_name (str): Name of the Gemini model
            rate_limiter (RateLimiter): Rate limiter instance
        """
        self.model_name = model_name
        self.rate_limiter = rate_limiter
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.request_count = 0
        self.error_count = 0
        
        logger.info(f"Initialized Gemini client for model: {model_name}")
    
    def generate_content(self, contents: str, **kwargs) -> Any:
        """
        Generate content using Gemini model with rate limiting and error handling
        
        Args:
            contents (str): Input content/prompt
            **kwargs: Additional parameters for the API call
            
        Returns:
            Response object from Gemini API
        """
        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()
            
            # Make API call
            start_time = time.time()
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                **kwargs
            )
            
            # Log successful request
            duration = time.time() - start_time
            self.request_count += 1
            
            logger.debug(f"Successful API call to {self.model_name} "
                        f"(duration: {duration:.2f}s, count: {self.request_count})")
            
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error calling {self.model_name}: {str(e)} "
                        f"(error count: {self.error_count})")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics
        
        Returns:
            dict: Client usage statistics
        """
        return {
            "model_name": self.model_name,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100
        }

class LLMClients:
    """
    Manager for both Pro and Lite Gemini clients
    """
    
    def __init__(self):
        """Initialize both Pro and Lite clients with separate rate limiters"""
        try:
            # Configure genai with API key
            # genai.configure(api_key=Config.GOOGLE_API_KEY)
            
            # Create rate limiters for each model
            self.pro_rate_limiter = RateLimiter(
                max_requests=Config.PRO_MODEL_RATE_LIMIT,
                time_window=60
            )
            
            self.lite_rate_limiter = RateLimiter(
                max_requests=Config.LITE_MODEL_RATE_LIMIT,
                time_window=60
            )
            
            # Initialize clients
            self.pro_client = GeminiClient(
                Config.GEMINI_PRO_MODEL,
                self.pro_rate_limiter
            )
            
            self.lite_client = GeminiClient(
                Config.GEMINI_LITE_MODEL,
                self.lite_rate_limiter
            )
            
            # Test connectivity
            self._test_connectivity()
            
            logger.info("LLM clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {str(e)}")
            raise
    
    def _test_connectivity(self):
        """Test connectivity to both models"""
        try:
            # Test Pro model
            test_response = self.pro_client.generate_content("Hello, respond with 'OK'")
            logger.info(f"Pro model connectivity test: {test_response.text[:20] if test_response.text else 'No response'}")
            
            # Small delay between tests
            time.sleep(1)
            
            # Test Lite model
            test_response = self.lite_client.generate_content("Hello, respond with 'OK'")
            logger.info(f"Lite model connectivity test: {test_response.text[:20] if test_response.text else 'No response'}")
            
        except Exception as e:
            logger.warning(f"Connectivity test failed: {str(e)}")
            # Don't raise here as the models might still work for actual requests
    
    def get_pro_client(self) -> GeminiClient:
        """
        Get the Pro model client (for complex reasoning tasks)
        
        Returns:
            GeminiClient: Pro model client
        """
        return self.pro_client
    
    def get_lite_client(self) -> GeminiClient:
        """
        Get the Lite model client (for conversational tasks)
        
        Returns:
            GeminiClient: Lite model client
        """
        return self.lite_client
    
    def get_client_stats(self) -> Dict[str, Any]:
        """
        Get statistics for both clients
        
        Returns:
            dict: Combined statistics
        """
        return {
            "pro_client": self.pro_client.get_stats(),
            "lite_client": self.lite_client.get_stats(),
            "total_requests": self.pro_client.request_count + self.lite_client.request_count,
            "total_errors": self.pro_client.error_count + self.lite_client.error_count
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on both clients
        
        Returns:
            dict: Health status
        """
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "clients": {}
        }
        
        # Check Pro client
        try:
            pro_stats = self.pro_client.get_stats()
            pro_healthy = pro_stats["success_rate"] > 80  # 80% success rate threshold
            
            health_status["clients"]["pro"] = {
                "status": "healthy" if pro_healthy else "degraded",
                "stats": pro_stats,
                "rate_limit_status": "ok" if self.pro_rate_limiter.can_make_request() else "limited"
            }
            
        except Exception as e:
            health_status["clients"]["pro"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check Lite client
        try:
            lite_stats = self.lite_client.get_stats()
            lite_healthy = lite_stats["success_rate"] > 80
            
            health_status["clients"]["lite"] = {
                "status": "healthy" if lite_healthy else "degraded", 
                "stats": lite_stats,
                "rate_limit_status": "ok" if self.lite_rate_limiter.can_make_request() else "limited"
            }
            
        except Exception as e:
            health_status["clients"]["lite"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            if health_status["overall_status"] == "healthy":
                health_status["overall_status"] = "degraded"
        
        # Overall status logic
        if (health_status["clients"].get("pro", {}).get("status") == "unhealthy" and 
            health_status["clients"].get("lite", {}).get("status") == "unhealthy"):
            health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    def reset_stats(self):
        """Reset statistics for both clients"""
        self.pro_client.request_count = 0
        self.pro_client.error_count = 0
        self.lite_client.request_count = 0
        self.lite_client.error_count = 0
        
        logger.info("Client statistics reset")

# Global instance for easy access
_llm_clients_instance = None

def get_llm_clients() -> LLMClients:
    """
    Get global LLM clients instance (singleton pattern)
    
    Returns:
        LLMClients: Global instance
    """
    global _llm_clients_instance
    
    if _llm_clients_instance is None:
        _llm_clients_instance = LLMClients()
    
    return _llm_clients_instance

def reset_llm_clients():
    """Reset the global LLM clients instance"""
    global _llm_clients_instance
    _llm_clients_instance = None

# Convenience functions for direct access
def get_pro_client() -> GeminiClient:
    """Get Pro model client directly"""
    return get_llm_clients().get_pro_client()

def get_lite_client() -> GeminiClient:
    """Get Lite model client directly"""
    return get_llm_clients().get_lite_client()