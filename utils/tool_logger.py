"""
Enhanced Tool Logging System for tracking all tool calls and responses
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from functools import wraps

# Configure tool-specific logger
tool_logger = logging.getLogger('tool_calls')
tool_handler = logging.StreamHandler()
tool_formatter = logging.Formatter(
    '%(asctime)s - TOOL_CALL - %(levelname)s - %(message)s'
)
tool_handler.setFormatter(tool_formatter)
tool_logger.addHandler(tool_handler)
tool_logger.setLevel(logging.INFO)

class ToolLogger:
    """
    Comprehensive logging system for all tool calls and responses
    """
    
    def __init__(self):
        self.call_history = []
        self.performance_metrics = {}
        
    def log_tool_call(self, 
                     tool_name: str, 
                     agent_name: str,
                     input_params: Dict[str, Any], 
                     response: Any, 
                     execution_time: float,
                     success: bool,
                     error: str = None) -> None:
        """
        Log detailed information about tool calls
        
        Args:
            tool_name (str): Name of the tool called
            agent_name (str): Name of the agent making the call
            input_params (dict): Parameters passed to the tool
            response (Any): Tool response
            execution_time (float): Time taken to execute
            success (bool): Whether the call was successful
            error (str): Error message if failed
        """
        
        call_record = {
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'agent_name': agent_name,
            'input_params': self._sanitize_params(input_params),
            'response_summary': self._summarize_response(response),
            'execution_time_ms': round(execution_time * 1000, 2),
            'success': success,
            'error': error
        }
        
        self.call_history.append(call_record)
        
        # Update performance metrics
        if tool_name not in self.performance_metrics:
            self.performance_metrics[tool_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_execution_time': 0,
                'average_execution_time': 0
            }
        
        metrics = self.performance_metrics[tool_name]
        metrics['total_calls'] += 1
        metrics['total_execution_time'] += execution_time
        metrics['average_execution_time'] = metrics['total_execution_time'] / metrics['total_calls']
        
        if success:
            metrics['successful_calls'] += 1
        else:
            metrics['failed_calls'] += 1
        
        # Log to console
        log_message = f"TOOL: {tool_name} | AGENT: {agent_name} | TIME: {execution_time*1000:.2f}ms | SUCCESS: {success}"
        if error:
            log_message += f" | ERROR: {error}"
            
        tool_logger.info(log_message)
        
        # Detailed parameter logging
        tool_logger.debug(f"TOOL PARAMS: {json.dumps(self._sanitize_params(input_params), indent=2)}")
        
        if not success:
            tool_logger.error(f"TOOL FAILURE - {tool_name}: {error}")
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for logging (truncate long strings, etc.)"""
        sanitized = {}
        for key, value in params.items():
            if isinstance(value, str) and len(value) > 200:
                sanitized[key] = value[:200] + "... (truncated)"
            elif isinstance(value, dict):
                sanitized[key] = {k: str(v)[:100] if isinstance(v, str) else v for k, v in value.items()}
            else:
                sanitized[key] = value
        return sanitized
    
    def _summarize_response(self, response: Any) -> Dict[str, Any]:
        """Create a summary of the response for logging"""
        if isinstance(response, str):
            return {
                'type': 'string',
                'length': len(response),
                'preview': response[:100] + "..." if len(response) > 100 else response
            }
        elif isinstance(response, dict):
            return {
                'type': 'dict',
                'keys': list(response.keys()),
                'size': len(response)
            }
        elif response is None:
            return {'type': 'None'}
        else:
            return {
                'type': str(type(response).__name__),
                'str_representation': str(response)[:100]
            }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report of all tool calls"""
        total_calls = sum(metrics['total_calls'] for metrics in self.performance_metrics.values())
        successful_calls = sum(metrics['successful_calls'] for metrics in self.performance_metrics.values())
        
        return {
            'summary': {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': total_calls - successful_calls,
                'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
                'tools_used': len(self.performance_metrics)
            },
            'per_tool_metrics': self.performance_metrics,
            'recent_calls': self.call_history[-10:]  # Last 10 calls
        }
    
    def get_tool_usage_summary(self, tool_name: str) -> Dict[str, Any]:
        """Get usage summary for a specific tool"""
        if tool_name not in self.performance_metrics:
            return {'error': f'No data for tool: {tool_name}'}
        
        metrics = self.performance_metrics[tool_name]
        tool_calls = [call for call in self.call_history if call['tool_name'] == tool_name]
        
        return {
            'tool_name': tool_name,
            'metrics': metrics,
            'recent_calls': tool_calls[-5:],  # Last 5 calls for this tool
            'common_errors': self._get_common_errors(tool_calls)
        }
    
    def _get_common_errors(self, tool_calls: list) -> Dict[str, int]:
        """Analyze common errors for a tool"""
        error_counts = {}
        for call in tool_calls:
            if not call['success'] and call['error']:
                error_type = call['error'][:50]  # First 50 chars of error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts

# Global logger instance
tool_logger_instance = ToolLogger()

def log_tool_call(tool_name: str, agent_name: str = "Unknown"):
    """
    Decorator for logging tool calls with detailed metrics
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error = None
            response = None
            
            try:
                response = func(*args, **kwargs)
                success = True
                return response
            except Exception as e:
                error = str(e)
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Extract meaningful parameters
                input_params = {
                    'args_count': len(args),
                    'kwargs': kwargs
                }
                
                tool_logger_instance.log_tool_call(
                    tool_name=tool_name,
                    agent_name=agent_name,
                    input_params=input_params,
                    response=response,
                    execution_time=execution_time,
                    success=success,
                    error=error
                )
        
        return wrapper
    return decorator