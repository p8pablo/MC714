"""
Gerador de tráfego para simular requisições chegando ao sistema
"""
import random
import simpy
import sys
import os
from typing import Callable, Any

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.request import Request
from config.settings import TrafficPattern


class TrafficGenerator:
    def __init__(self, env: simpy.Environment, 
                 request_callback: Callable[[Request], Any],
                 pattern: TrafficPattern = TrafficPattern.CONSTANT):
        self.env = env
        self.request_callback = request_callback
        self.pattern = pattern
        self.request_counter = 0
        self.generated_requests = []
        
    def set_pattern(self, pattern: TrafficPattern):
        """Altera o padrão de tráfego"""
        self.pattern = pattern
        print(f"Padrão de tráfego alterado para: {pattern.value}")
        
    def generate_traffic(self, duration: float, base_rate: float = 2.0):
        """
        Gera tráfego durante um período especificado
        
        Args:
            duration: Duração da geração de tráfego
            base_rate: Taxa base de requisições por segundo
        """
        print(f"Iniciando geração de tráfego: {self.pattern.value} por {duration}s")
        
        if self.pattern == TrafficPattern.CONSTANT:
            yield from self._generate_constant_traffic(duration, base_rate)
        elif self.pattern == TrafficPattern.BURST:
            yield from self._generate_burst_traffic(duration, base_rate)
        else:
            raise ValueError(f"Padrão não suportado: {self.pattern}")
    
    def _generate_constant_traffic(self, duration: float, rate: float):
        """Gera tráfego constante"""
        end_time = self.env.now + duration
        
        while self.env.now < end_time:
            # Intervalo entre requisições segue distribuição exponencial
            interval = random.expovariate(rate)
            yield self.env.timeout(interval)
            
            if self.env.now >= end_time:
                break
                
            self._create_and_send_request()
    
    def _generate_burst_traffic(self, duration: float, base_rate: float):
        """Gera tráfego com rajadas"""
        end_time = self.env.now + duration
        
        while self.env.now < end_time:
            # Decide se será uma rajada ou período normal
            is_burst = random.random() < 0.3  # 30% de chance de rajada
            
            if is_burst:
                # Rajada: alta taxa por período curto
                burst_duration = random.uniform(2.0, 5.0)  # 2-5 segundos
                burst_rate = base_rate * random.uniform(5.0, 10.0)  # 5-10x mais requisições
                burst_end = min(self.env.now + burst_duration, end_time)
                
                print(f"[BURST] Iniciando rajada às {self.env.now:.2f}s (taxa: {burst_rate:.2f} req/s)")
                
                while self.env.now < burst_end:
                    interval = random.expovariate(burst_rate)
                    yield self.env.timeout(interval)
                    
                    if self.env.now >= burst_end or self.env.now >= end_time:
                        break
                        
                    self._create_and_send_request()
                    
                print(f"[BURST] Fim da rajada às {self.env.now:.2f}s")
                
                # Período de calmaria após rajada
                calm_period = random.uniform(3.0, 8.0)
                yield self.env.timeout(calm_period)
                
            else:
                # Período normal
                normal_duration = random.uniform(5.0, 15.0)
                normal_end = min(self.env.now + normal_duration, end_time)
                
                while self.env.now < normal_end:
                    interval = random.expovariate(base_rate)
                    yield self.env.timeout(interval)
                    
                    if self.env.now >= normal_end or self.env.now >= end_time:
                        break
                        
                    self._create_and_send_request()
    
    def _create_and_send_request(self):
        """Cria e envia uma nova requisição"""
        self.request_counter += 1
        request = Request.create_random(self.request_counter, self.env.now)
        self.generated_requests.append(request)
        
        print(f"Tempo {self.env.now:.2f}: Gerada requisição {request.id} ({request.type.value})")
        
        # Envia para o callback (load balancer)
        self.request_callback(request)
    
    def get_statistics(self) -> dict:
        """Retorna estatísticas da geração de tráfego"""
        if not self.generated_requests:
            return {
                "total_requests": 0,
                "pattern": self.pattern.value,
                "avg_arrival_rate": 0.0,
                "request_types": {}
            }
        
        # Calcula taxa média de chegada
        first_request = min(req.arrival_time for req in self.generated_requests)
        last_request = max(req.arrival_time for req in self.generated_requests)
        time_span = max(last_request - first_request, 1.0)
        avg_rate = len(self.generated_requests) / time_span
        
        # Conta tipos de requisição
        type_counts = {}
        for req in self.generated_requests:
            type_name = req.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "total_requests": len(self.generated_requests),
            "pattern": self.pattern.value,
            "avg_arrival_rate": avg_rate,
            "request_types": type_counts,
            "time_span": time_span
        }