"""
Sistema de análise e relatórios de métricas
"""
from typing import Dict, List, Any
import json
from datetime import datetime


class MetricsAnalyzer:
    def __init__(self):
        self.simulation_results = []
    
    def add_simulation_result(self, result: Dict[str, Any], experiment_name: str = ""):
        """Adiciona resultado de uma simulação"""
        result["experiment_name"] = experiment_name
        result["timestamp"] = datetime.now().isoformat()
        self.simulation_results.append(result)
    
    def compare_policies(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compara performance entre diferentes políticas"""
        comparison = {
            "policies_compared": [],
            "metrics_comparison": {},
            "best_policy": {},
            "summary": {}
        }
        
        for result in results:
            policy = result["load_balancer_stats"]["policy"]
            comparison["policies_compared"].append(policy)
            
            system_metrics = result["system_metrics"]
            
            if policy not in comparison["metrics_comparison"]:
                comparison["metrics_comparison"][policy] = {}
            
            comparison["metrics_comparison"][policy].update({
                "throughput": system_metrics["system_throughput"],
                "avg_response_time": system_metrics["avg_response_time"],
                "avg_waiting_time": system_metrics["avg_waiting_time"],
                "utilization": system_metrics["system_utilization"],
                "response_time_std": system_metrics["response_time_std"],
                "total_processed": system_metrics["total_processed"]
            })
        
        # Determina melhor política para cada métrica
        comparison["best_policy"] = self._find_best_policies(comparison["metrics_comparison"])
        
        # Resumo geral
        comparison["summary"] = self._generate_policy_summary(comparison["metrics_comparison"])
        
        return comparison
    
    def _find_best_policies(self, metrics: Dict[str, Dict[str, float]]) -> Dict[str, str]:
        """Encontra a melhor política para cada métrica"""
        best = {}
        
        # Throughput - maior é melhor
        max_throughput = max(metrics[policy]["throughput"] for policy in metrics)
        for policy in metrics:
            if metrics[policy]["throughput"] == max_throughput:
                best["throughput"] = policy
                break
        
        # Response time - menor é melhor
        min_response_time = min(metrics[policy]["avg_response_time"] for policy in metrics)
        for policy in metrics:
            if metrics[policy]["avg_response_time"] == min_response_time:
                best["avg_response_time"] = policy
                break
        
        # Waiting time - menor é melhor
        min_waiting_time = min(metrics[policy]["avg_waiting_time"] for policy in metrics)
        for policy in metrics:
            if metrics[policy]["avg_waiting_time"] == min_waiting_time:
                best["avg_waiting_time"] = policy
                break
        
        # Utilization - maior é melhor (mas não muito próximo de 1)
        utilizacoes = {policy: metrics[policy]["utilization"] for policy in metrics}
        best_util_policy = max(utilizacoes, key=utilizacoes.get)
        best["utilization"] = best_util_policy
        
        return best
    
    def _generate_policy_summary(self, metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Gera resumo das políticas"""
        summary = {}
        
        for policy in metrics:
            policy_metrics = metrics[policy]
            
            # Score baseado em múltiplas métricas (0-100)
            # Normaliza métricas e calcula score ponderado
            throughput_score = min(policy_metrics["throughput"] * 10, 100)  # Assume max ~10 req/s
            response_score = max(0, 100 - policy_metrics["avg_response_time"] * 20)  # Penaliza response time alto
            waiting_score = max(0, 100 - policy_metrics["avg_waiting_time"] * 30)  # Penaliza waiting time alto
            util_score = policy_metrics["utilization"] * 100  # Utilização como percentual
            
            overall_score = (throughput_score * 0.3 + response_score * 0.3 + 
                           waiting_score * 0.2 + util_score * 0.2)
            
            summary[policy] = {
                "overall_score": round(overall_score, 2),
                "strengths": [],
                "weaknesses": [],
                "recommended_for": ""
            }
            
            # Identifica pontos fortes e fracos
            if policy_metrics["throughput"] > 2.0:
                summary[policy]["strengths"].append("Alto throughput")
            if policy_metrics["avg_response_time"] < 1.0:
                summary[policy]["strengths"].append("Baixo tempo de resposta")
            if policy_metrics["avg_waiting_time"] < 0.5:
                summary[policy]["strengths"].append("Baixo tempo de espera")
            if policy_metrics["utilization"] > 0.7:
                summary[policy]["strengths"].append("Boa utilização de recursos")
            
            if policy_metrics["throughput"] < 1.5:
                summary[policy]["weaknesses"].append("Throughput baixo")
            if policy_metrics["avg_response_time"] > 2.0:
                summary[policy]["weaknesses"].append("Tempo de resposta alto")
            if policy_metrics["utilization"] < 0.5:
                summary[policy]["weaknesses"].append("Subutilização de recursos")
            
            # Recomendações de uso
            if policy == "random":
                summary[policy]["recommended_for"] = "Cargas uniformes e simples implementação"
            elif policy == "round_robin":
                summary[policy]["recommended_for"] = "Distribuição equitativa e servidores homogêneos"
            elif policy == "shortest_queue":
                summary[policy]["recommended_for"] = "Cargas heterogêneas e otimização de latência"
        
        return summary
    
    def analyze_traffic_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa performance sob diferentes padrões de tráfego"""
        analysis = {
            "patterns_analyzed": [],
            "pattern_performance": {},
            "recommendations": {}
        }
        
        for result in results:
            pattern = result["traffic_stats"]["pattern"]
            analysis["patterns_analyzed"].append(pattern)
            
            if pattern not in analysis["pattern_performance"]:
                analysis["pattern_performance"][pattern] = []
            
            analysis["pattern_performance"][pattern].append({
                "policy": result["load_balancer_stats"]["policy"],
                "throughput": result["system_metrics"]["system_throughput"],
                "response_time": result["system_metrics"]["avg_response_time"],
                "utilization": result["system_metrics"]["system_utilization"]
            })
        
        # Gera recomendações para cada padrão
        for pattern in analysis["pattern_performance"]:
            pattern_data = analysis["pattern_performance"][pattern]
            best_policy = max(pattern_data, key=lambda x: x["throughput"])
            
            analysis["recommendations"][pattern] = {
                "best_policy": best_policy["policy"],
                "reason": f"Melhor throughput ({best_policy['throughput']:.2f} req/s) para padrão {pattern}"
            }
        
        return analysis
    
    def generate_report(self, output_file: str = "simulation_report.json"):
        """Gera relatório completo em JSON"""
        if not self.simulation_results:
            return {"error": "Nenhum resultado de simulação disponível"}
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "total_simulations": len(self.simulation_results),
            "simulation_results": self.simulation_results
        }
        
        # Análise comparativa se houver múltiplas simulações
        if len(self.simulation_results) > 1:
            report["policy_comparison"] = self.compare_policies(self.simulation_results)
            report["traffic_analysis"] = self.analyze_traffic_patterns(self.simulation_results)
        
        # Salva arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Relatório salvo em: {output_file}")
        return report
    
    def print_summary(self, result: Dict[str, Any]):
        """Imprime resumo da simulação na tela"""
        print(f"\n{'='*80}")
        print(f"RESUMO DA SIMULAÇÃO")
        print(f"{'='*80}")
        
        # Informações gerais
        print(f"Tempo de simulação: {result['simulation_time']:.2f}s")
        print(f"Política: {result['load_balancer_stats']['policy']}")
        print(f"Padrão de tráfego: {result['traffic_stats']['pattern']}")
        
        # Métricas do sistema
        sys_metrics = result["system_metrics"]
        print(f"\n📊 MÉTRICAS DO SISTEMA:")
        print(f"  • Throughput: {sys_metrics['system_throughput']:.3f} req/s")
        print(f"  • Tempo médio de resposta: {sys_metrics['avg_response_time']:.3f}s")
        print(f"  • Tempo médio de espera: {sys_metrics['avg_waiting_time']:.3f}s")
        print(f"  • Utilização do sistema: {sys_metrics['system_utilization']:.1%}")
        print(f"  • Total processado: {sys_metrics['total_processed']} requisições")
        
        # Métricas dos servidores
        print(f"\n🖥️  MÉTRICAS DOS SERVIDORES:")
        for server_metric in result["server_metrics"]:
            print(f"  Server {server_metric['server_id']}:")
            print(f"    - Requisições processadas: {server_metric['processed_count']}")
            print(f"    - Throughput: {server_metric['throughput']:.3f} req/s")
            print(f"    - Tempo médio de resposta: {server_metric['avg_response_time']:.3f}s")
        
        # Distribuição de carga
        lb_stats = result["load_balancer_stats"]
        print(f"\n⚖️  DISTRIBUIÇÃO DE CARGA:")
        print(f"  • Política: {lb_stats['policy']}")
        print(f"  • Requisições distribuídas: {lb_stats['total_requests_distributed']}")
        print(f"  • Distribuição por servidor:")
        for server_id, count in lb_stats['requests_per_server'].items():
            percentage = (count / lb_stats['total_requests_distributed']) * 100 if lb_stats['total_requests_distributed'] > 0 else 0
            print(f"    - Server {server_id}: {count} ({percentage:.1f}%)")
        print(f"  • Variância da distribuição: {lb_stats['distribution_variance']:.3f}")
        
        print(f"{'='*80}")
    
    def clear_results(self):
        """Limpa resultados armazenados"""
        self.simulation_results = []