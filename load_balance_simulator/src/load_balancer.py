"""
Load Balancer com diferentes políticas de balanceamento
"""
import random
import sys
import os
from typing import List

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.server import Server
from models.request import Request
from config.settings import LoadBalancingPolicy


class LoadBalancer:
    def __init__(self, servers: List[Server], policy: LoadBalancingPolicy = LoadBalancingPolicy.ROUND_ROBIN):
        self.servers = servers
        self.policy = policy
        self.round_robin_index = 0
        self.total_requests = 0
        
    def set_policy(self, policy: LoadBalancingPolicy):
        """Altera a política de balanceamento"""
        self.policy = policy
        print(f"Política de balanceamento alterada para: {policy.value}")
        
    def select_server(self, request: Request) -> Server:
        """Seleciona servidor baseado na política configurada"""
        self.total_requests += 1
        
        if self.policy == LoadBalancingPolicy.RANDOM:
            return self._select_random()
        elif self.policy == LoadBalancingPolicy.ROUND_ROBIN:
            return self._select_round_robin()
        elif self.policy == LoadBalancingPolicy.SHORTEST_QUEUE:
            return self._select_shortest_queue()
        else:
            raise ValueError(f"Política não suportada: {self.policy}")
    
    def _select_random(self) -> Server:
        """Política de escolha aleatória"""
        selected = random.choice(self.servers)
        print(f"[RANDOM] Requisição {self.total_requests} -> Server {selected.id}")
        return selected
    
    def _select_round_robin(self) -> Server:
        """Política Round Robin"""
        selected = self.servers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.servers)
        print(f"[ROUND_ROBIN] Requisição {self.total_requests} -> Server {selected.id}")
        return selected
    
    def _select_shortest_queue(self) -> Server:
        """Política de fila mais curta"""
        selected = min(self.servers, key=lambda s: s.get_queue_length())
        print(f"[SHORTEST_QUEUE] Requisição {self.total_requests} -> Server {selected.id} (fila: {selected.get_queue_length()})")
        return selected
    
    def get_status(self) -> dict:
        """Retorna status atual dos servidores"""
        return {
            "policy": self.policy.value,
            "total_requests": self.total_requests,
            "servers": [
                {
                    "id": server.id,
                    "queue_length": server.get_queue_length(),
                    "current_load": server.get_current_load(),
                    "is_busy": server.is_busy()
                }
                for server in self.servers
            ]
        }
    
    def get_distribution_stats(self) -> dict:
        """Estatísticas de distribuição de carga"""
        server_requests = {}
        for server in self.servers:
            server_requests[server.id] = len(server.processed_requests)
        
        return {
            "policy": self.policy.value,
            "total_requests_distributed": self.total_requests,
            "requests_per_server": server_requests,
            "distribution_variance": self._calculate_variance(list(server_requests.values()))
        }
    
    def _calculate_variance(self, values: List[int]) -> float:
        """Calcula variância da distribuição"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)