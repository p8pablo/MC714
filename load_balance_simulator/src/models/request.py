"""
Classe request para representar requisições no sistema
"""
import random
from dataclasses import dataclass
from typing import Optional
from config.settings import RequestType, REQUEST_CONFIG

@dataclass
class Request:    
    id: int
    type: RequestType
    arrival_time: float
    processing_time: float
    start_processing_time: Optional[float] = None
    completion_time: Optional[float] = None
    server_id: Optional[int] = None
    
    @classmethod
    def create_random(cls, request_id: int, arrival_time: float) -> 'Request':
        req_type = random.choice(list(RequestType))
        
        if req_type == RequestType.CPU_INTENSIVE:
            config = REQUEST_CONFIG["cpu_intensive"]
        else:
            config = REQUEST_CONFIG["io_intensive"]
        
        processing_time = random.uniform(
            config["min_processing_time"],
            config["max_processing_time"]
        )
        
        return cls(
            id=request_id,
            type=req_type,
            arrival_time=arrival_time,
            processing_time=processing_time
        )
        
    def get_response_time(self) -> Optional[float]:
        """Tempo total de resposta (fim - chegada)"""
        if self.completion_time is not None:
            return self.completion_time - self.arrival_time
        return None
    
    def get_waiting_time(self) -> Optional[float]:
        """Tempo de espera na fila (início processamento - chegada)"""
        if self.start_processing_time is not None:
            return self.start_processing_time - self.arrival_time
        return None
    
    def get_actual_processing_time(self) -> Optional[float]:
        """Calcula o tempo real de processamento"""
        if (self.start_processing_time is not None and 
            self.completion_time is not None):
            return self.completion_time - self.start_processing_time
        return None
    
    def is_completed(self) -> bool:
        """Verifica se a requisição foi completada"""
        return self.completion_time is not None
    
    def __str__(self) -> str:
        """Log da requisição"""
        status = "Completed" if self.is_completed() else "Pending"
        return f"Request({self.id}, {self.type.value}, {status})"
    
