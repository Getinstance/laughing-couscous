"""
Monitoring and logging module for production API.
"""

import logging
import json
import time
from datetime import datetime
from functools import wraps
from typing import Callable, Any
import psutil
import os


class ProductionLogger:
    """Logger for production monitoring."""
    
    def __init__(self, name: str, log_file: str = "logs/app.log"):
        """Initialize logger."""
        self.name = name
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Log API request."""
        self.logger.info(
            f"Request | Endpoint: {endpoint} | Method: {method} | "
            f"Status: {status_code} | Duration: {duration:.3f}s"
        )
    
    def log_error(self, error_type: str, error_msg: str, endpoint: str = None):
        """Log errors."""
        if endpoint:
            self.logger.error(
                f"Error | Type: {error_type} | Endpoint: {endpoint} | Message: {error_msg}"
            )
        else:
            self.logger.error(f"Error | Type: {error_type} | Message: {error_msg}")
    
    def log_prediction(self, symbol: str, predicted_price: float, confidence: str):
        """Log prediction."""
        self.logger.info(
            f"Prediction | Symbol: {symbol} | Predicted Price: ${predicted_price:.2f} | "
            f"Confidence: {confidence}"
        )


class PerformanceMonitor:
    """Monitor system and API performance."""
    
    def __init__(self):
        """Initialize monitor."""
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.predictions_made = 0
    
    def get_system_metrics(self) -> dict:
        """Get current system metrics."""
        process = psutil.Process(os.getpid())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': process.cpu_percent(interval=1),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'uptime_seconds': time.time() - self.start_time,
        }
    
    def get_api_metrics(self) -> dict:
        """Get API performance metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 
            else 0
        )
        
        error_rate = (
            self.error_count / self.request_count 
            if self.request_count > 0 
            else 0
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': error_rate * 100,
            'avg_response_time_ms': avg_response_time * 1000,
            'predictions_made': self.predictions_made,
        }
    
    def record_request(self, duration: float, success: bool = True):
        """Record request metrics."""
        self.request_count += 1
        self.total_response_time += duration
        if not success:
            self.error_count += 1
    
    def record_prediction(self):
        """Record prediction."""
        self.predictions_made += 1
    
    def get_all_metrics(self) -> dict:
        """Get all metrics."""
        return {
            'system': self.get_system_metrics(),
            'api': self.get_api_metrics(),
        }


class MetricsCollector:
    """Collect and store metrics."""
    
    def __init__(self, metrics_file: str = "logs/metrics.jsonl"):
        """Initialize collector."""
        self.metrics_file = metrics_file
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
    
    def record(self, data: dict):
        """Record metrics to file."""
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Error recording metrics: {str(e)}")
    
    def get_latest(self, n: int = 100) -> list:
        """Get latest n metrics."""
        try:
            with open(self.metrics_file, 'r') as f:
                lines = f.readlines()
                return [json.loads(line) for line in lines[-n:]]
        except Exception as e:
            print(f"Error reading metrics: {str(e)}")
            return []


def monitor_performance(logger: ProductionLogger, monitor: PerformanceMonitor):
    """Decorator to monitor endpoint performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_request(duration, success=True)
                logger.logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_request(duration, success=False)
                logger.log_error("ExecutionError", str(e), endpoint=func.__name__)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_request(duration, success=True)
                logger.logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_request(duration, success=False)
                logger.log_error("ExecutionError", str(e), endpoint=func.__name__)
                raise
        
        # Return async wrapper if function is async
        return async_wrapper if hasattr(func, '__await__') else sync_wrapper
    
    return decorator


# Global instances
logger = ProductionLogger("StockPredictionAPI")
monitor = PerformanceMonitor()
metrics_collector = MetricsCollector()
