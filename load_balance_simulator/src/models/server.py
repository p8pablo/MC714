"""
Classe Server para simular servidores no sistema
"""
import simpy
from typing import List, Dict, Any
from .request import Request
from config.settings import SERVER_CONFIG

class Server:    
    def __init__(self, env: simpy.Environment, server_id: int, 
                 capacity: int = None, cpu_power: float = None):
        self.env = env
        self.id = server_id
        self.capacity = capacity or SERVER_CONFIG["default_capacity"]
        self.cpu_power = cpu_power or SERVER_CONFIG["default_cpu_power"]
        
        self.resource = simpy.Resource(env, capacity=self.capacity)
        
        self.processed_requests: List[Request] = []
        self.total_processing_time = 0.0
        self.total_waiting_time = 0.0
        
        self.current_requests = 0
        
    def process_request(self, request: Request):
        # Marca início do processamento
        request.start_processing_time = self.env.now
        request.server_id = self.id
        
        # Calcula tempo de processamento ajustado pela velocidade do CPU
        processing_time = request.processing_time / self.cpu_power
        
        # Debug log
        print(f"Tempo {self.env.now:.2f}: Server {self.id} iniciou processamento da requisição {request.id}")
        
        # Simula processamento
        yield self.env.timeout(processing_time)
        
        # Marca conclusão
        request.completion_time = self.env.now
        self.processed_requests.append(request)
        
        # Atualiza estatísticas
        self.total_processing_time += processing_time
        if request.get_waiting_time():
            self.total_waiting_time += request.get_waiting_time()
        
        print(f"Tempo {self.env.now:.2f}: Server {self.id} completou requisição {request.id} (processamento: {processing_time:.3f}s)")
    
    def get_queue_length(self) -> int:
        # Tamanho da fila de espera
        return len(self.resource.queue)
    
    def get_current_load(self) -> float:
        # Carga atual do servidor (0 a 1)
        return len(self.resource.users) / self.capacity
    
    def is_busy(self) -> bool:
        # Verifica se o servidor está ocupado
        return len(self.resource.users) > 0
    
    def get_metrics(self) -> Dict[str, Any]:
        # Retorna métricas do servidor
        if not self.processed_requests:
            return {
                "server_id": self.id,
                "processed_count": 0,
                "avg_response_time": 0.0,
                "avg_waiting_time": 0.0,
                "avg_processing_time": 0.0,
                "current_queue_length": self.get_queue_length(),
                "current_load": self.get_current_load(),
                "throughput": 0.0,
                "cpu_power": self.cpu_power,
                "capacity": self.capacity
            }
        
        # Calcula métricas
        response_times = [req.get_response_time() for req in self.processed_requests 
                         if req.get_response_time() is not None]
        waiting_times = [req.get_waiting_time() for req in self.processed_requests 
                        if req.get_waiting_time() is not None]
        processing_times = [req.get_actual_processing_time() for req in self.processed_requests 
                           if req.get_actual_processing_time() is not None]
        
        # Calcula throughput (requisições por unidade de tempo)
        if self.processed_requests:
            first_completion = min(req.completion_time for req in self.processed_requests)
            last_completion = max(req.completion_time for req in self.processed_requests)
            time_span = max(last_completion - first_completion, 1.0)  # Evita divisão por zero
            throughput = len(self.processed_requests) / time_span
        else:
            throughput = 0.0
        
        return {
            "server_id": self.id,
            "processed_count": len(self.processed_requests),
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0.0,
            "avg_waiting_time": sum(waiting_times) / len(waiting_times) if waiting_times else 0.0,
            "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0.0,
            "current_queue_length": self.get_queue_length(),
            "current_load": self.get_current_load(),
            "throughput": throughput,
            "cpu_power": self.cpu_power,
            "capacity": self.capacity,
            "total_processing_time": self.total_processing_time
        }
    
    def __str__(self) -> str:
        """Log do servidor"""
        return f"Server({self.id}, queue={self.get_queue_length()}, load={self.get_current_load():.1%})"
    
    def __repr__(self) -> str:
        return self.__str__()
