"""
Módulo de monitoramento e logging para API de produção.
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
    """Logger para monitoramento de produção."""
    
    def __init__(self, name: str, log_file: str = "logs/app.log"):
        """Inicializa o logger."""
        self.name = name
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura logger com manipuladores de arquivo e console."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Cria diretório de logs se não existir
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Manipulador de arquivo
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Manipulador de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatador
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
        """Log de requisição da API."""
        self.logger.info(
            f"Requisição | Endpoint: {endpoint} | Método: {method} | "
            f"Status: {status_code} | Duração: {duration:.3f}s"
        )
    
    def log_error(self, error_type: str, error_msg: str, endpoint: str = None):
        """Log de erros."""
        if endpoint:
            self.logger.error(
                f"Erro | Tipo: {error_type} | Endpoint: {endpoint} | Mensagem: {error_msg}"
            )
        else:
            self.logger.error(f"Erro | Tipo: {error_type} | Mensagem: {error_msg}")
    
    def log_prediction(self, symbol: str, predicted_price: float, confidence: str):
        """Log de previsão."""
        self.logger.info(
            f"Previsão | Símbolo: {symbol} | Preço Previsto: ${predicted_price:.2f} | "
            f"Confiança: {confidence}"
        )


class PerformanceMonitor:
    """Monitora desempenho do sistema e da API."""
    
    def __init__(self):
        """Inicializa o monitor."""
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.predictions_made = 0
    
    def get_system_metrics(self) -> dict:
        """Obtém métricas atuais do sistema."""
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
        """Obtém métricas de desempenho da API."""
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
        """Registra métricas de requisição."""
        self.request_count += 1
        self.total_response_time += duration
        if not success:
            self.error_count += 1
    
    def record_prediction(self):
        """Registra previsão."""
        self.predictions_made += 1
    
    def get_all_metrics(self) -> dict:
        """Obtém todas as métricas."""
        return {
            'system': self.get_system_metrics(),
            'api': self.get_api_metrics(),
        }


class MetricsCollector:
    """Coleta e armazena métricas."""
    
    def __init__(self, metrics_file: str = "logs/metrics.jsonl"):
        """Inicializa o coletor."""
        self.metrics_file = metrics_file
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
    
    def record(self, data: dict):
        """Registra métricas em arquivo."""
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"Erro ao registrar métricas: {str(e)}")
    
    def get_latest(self, n: int = 100) -> list:
        """Obtém as últimas n métricas."""
        try:
            with open(self.metrics_file, 'r') as f:
                lines = f.readlines()
                return [json.loads(line) for line in lines[-n:]]
        except Exception as e:
            print(f"Erro ao ler métricas: {str(e)}")
            return []


def monitor_performance(logger: ProductionLogger, monitor: PerformanceMonitor):
    """Decorador para monitorar desempenho do endpoint."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_request(duration, success=True)
                logger.logger.debug(f"{func.__name__} concluído em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_request(duration, success=False)
                logger.log_error("ErroDeExecução", str(e), endpoint=func.__name__)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_request(duration, success=True)
                logger.logger.debug(f"{func.__name__} concluído em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_request(duration, success=False)
                logger.log_error("ErroDeExecução", str(e), endpoint=func.__name__)
                raise
        
        # Retorna wrapper assincronismo se a função for assincronismo
        return async_wrapper if hasattr(func, '__await__') else sync_wrapper
    
    return decorator


# Instâncias globais
logger = ProductionLogger("StockPredictionAPI")
monitor = PerformanceMonitor()
metrics_collector = MetricsCollector()
