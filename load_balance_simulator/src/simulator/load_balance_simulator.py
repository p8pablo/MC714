"""
Sistema de simulação principal que coordena load balancer, servidores e tráfego
"""
import simpy
from typing import List, Dict, Any
import sys
import os

# Adiciona o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.server import Server
from models.request import Request
from load_balancer import LoadBalancer
from traffic_generator import TrafficGenerator
from config.settings import LoadBalancingPolicy, TrafficPattern


class LoadBalanceSimulator:
    def __init__(self, num_servers: int = 3):
        self.env = simpy.Environment()
        self.num_servers = num_servers
        
        # Criar servidores
        self.servers = [
            Server(self.env, server_id=i, capacity=1, cpu_power=1.0) 
            for i in range(num_servers)
        ]
        
        # Criar load balancer
        self.load_balancer = LoadBalancer(
            self.servers, 
            LoadBalancingPolicy.ROUND_ROBIN
        )
        
        # Criar traffic generator
        self.traffic_generator = TrafficGenerator(
            self.env,
            self.handle_request,
            TrafficPattern.CONSTANT
        )
        
        self.active_processes = []
        
    def handle_request(self, request: Request):
        """Processa uma nova requisição através do load balancer"""
        # Seleciona servidor usando load balancer
        selected_server = self.load_balancer.select_server(request)
        
        # Inicia processo de atendimento no servidor
        process = self.env.process(self._process_request_on_server(selected_server, request))
        self.active_processes.append(process)
        
    def _process_request_on_server(self, server: Server, request: Request):
        """Processa requisição em um servidor específico"""
        with server.resource.request() as req:
            yield req
            yield from server.process_request(request)
    
    def run_simulation(self, 
                      duration: float = 100.0,
                      traffic_rate: float = 2.0,
                      policy: LoadBalancingPolicy = LoadBalancingPolicy.ROUND_ROBIN,
                      traffic_pattern: TrafficPattern = TrafficPattern.CONSTANT) -> Dict[str, Any]:
        """
        Executa uma simulação completa
        
        Args:
            duration: Duração da simulação em segundos
            traffic_rate: Taxa de requisições por segundo
            policy: Política de balanceamento
            traffic_pattern: Padrão de tráfego
        
        Returns:
            Resultados da simulação
        """
        print(f"\n{'='*60}")
        print(f"INICIANDO SIMULAÇÃO")
        print(f"Duração: {duration}s")
        print(f"Política: {policy.value}")
        print(f"Padrão de tráfego: {traffic_pattern.value}")
        print(f"Taxa base: {traffic_rate} req/s")
        print(f"Servidores: {self.num_servers}")
        print(f"{'='*60}")
        
        # Configurar políticas
        self.load_balancer.set_policy(policy)
        self.traffic_generator.set_pattern(traffic_pattern)
        
        # Iniciar geração de tráfego
        traffic_process = self.env.process(
            self.traffic_generator.generate_traffic(duration, traffic_rate)
        )
        
        # Executar simulação
        self.env.run(until=duration)
        
        print(f"\n{'='*60}")
        print(f"SIMULAÇÃO CONCLUÍDA às {self.env.now:.2f}s")
        print(f"{'='*60}")
        
        # Aguardar processos ativos terminarem
        if self.active_processes:
            print("Aguardando processos ativos terminarem...")
            # Simples timeout para finalizar processos pendentes
            timeout_counter = 0
            while self.active_processes and timeout_counter < 5:
                try:
                    self.env.run(until=self.env.now + 0.1)
                    timeout_counter += 0.1
                except simpy.StopSimulation:
                    break
                # Remove processos finalizados
                self.active_processes = [p for p in self.active_processes if not p.processed]
        
        # Coletar e retornar resultados
        return self.collect_results()
    
    def collect_results(self) -> Dict[str, Any]:
        """Coleta todos os resultados da simulação"""
        # Métricas dos servidores
        server_metrics = []
        for server in self.servers:
            server_metrics.append(server.get_metrics())
        
        # Métricas do load balancer
        lb_stats = self.load_balancer.get_distribution_stats()
        
        # Métricas do traffic generator
        traffic_stats = self.traffic_generator.get_statistics()
        
        # Métricas globais do sistema
        all_requests = []
        for server in self.servers:
            all_requests.extend(server.processed_requests)
        
        system_metrics = self._calculate_system_metrics(all_requests)
        
        return {
            "simulation_time": self.env.now,
            "system_metrics": system_metrics,
            "server_metrics": server_metrics,
            "load_balancer_stats": lb_stats,
            "traffic_stats": traffic_stats
        }
    
    def _calculate_system_metrics(self, requests: List[Request]) -> Dict[str, Any]:
        """Calcula métricas globais do sistema"""
        if not requests:
            return {
                "total_processed": 0,
                "system_throughput": 0.0,
                "avg_response_time": 0.0,
                "avg_waiting_time": 0.0,
                "system_utilization": 0.0
            }
        
        # Tempos de resposta
        response_times = [req.get_response_time() for req in requests 
                         if req.get_response_time() is not None]
        
        # Tempos de espera
        waiting_times = [req.get_waiting_time() for req in requests 
                        if req.get_waiting_time() is not None]
        
        # Throughput do sistema
        first_completion = min(req.completion_time for req in requests)
        last_completion = max(req.completion_time for req in requests)
        time_span = max(last_completion - first_completion, 1.0)
        system_throughput = len(requests) / time_span
        
        # Utilização do sistema
        total_processing_time = sum(
            server.total_processing_time for server in self.servers
        )
        system_utilization = total_processing_time / (self.env.now * self.num_servers)
        
        return {
            "total_processed": len(requests),
            "system_throughput": system_throughput,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0.0,
            "avg_waiting_time": sum(waiting_times) / len(waiting_times) if waiting_times else 0.0,
            "system_utilization": system_utilization,
            "response_time_std": self._calculate_std(response_times) if len(response_times) > 1 else 0.0
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calcula desvio padrão"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def reset_simulation(self):
        """Reseta o simulador para nova simulação"""
        self.env = simpy.Environment()
        
        # Recriar servidores
        self.servers = [
            Server(self.env, server_id=i, capacity=1, cpu_power=1.0) 
            for i in range(self.num_servers)
        ]
        
        # Recriar load balancer
        self.load_balancer = LoadBalancer(
            self.servers, 
            LoadBalancingPolicy.ROUND_ROBIN
        )
        
        # Recriar traffic generator
        self.traffic_generator = TrafficGenerator(
            self.env,
            self.handle_request,
            TrafficPattern.CONSTANT
        )
        
        self.active_processes = []