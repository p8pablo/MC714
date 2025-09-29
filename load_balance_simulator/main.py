#!/usr/bin/env python3
"""
Simulador de Load Balance - MC714
Sistema de simulação para avaliar diferentes políticas de balanceamento de carga

Políticas implementadas:
- Escolha Aleatória (Random)
- Round Robin  
- Fila Mais Curta (Shortest Queue)

Autores: [Seus nomes]
Data: Setembro 2024
"""

import sys
import os
from typing import List, Dict, Any

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.simulator.load_balance_simulator import LoadBalanceSimulator
from src.metrics_analyzer import MetricsAnalyzer
from config.settings import LoadBalancingPolicy, TrafficPattern


def run_single_simulation(duration: float = 100.0, 
                         traffic_rate: float = 3.0,
                         policy: LoadBalancingPolicy = LoadBalancingPolicy.ROUND_ROBIN,
                         traffic_pattern: TrafficPattern = TrafficPattern.CONSTANT,
                         num_servers: int = 3) -> Dict[str, Any]:
    """Executa uma simulação única"""
    simulator = LoadBalanceSimulator(num_servers=num_servers)
    result = simulator.run_simulation(
        duration=duration,
        traffic_rate=traffic_rate, 
        policy=policy,
        traffic_pattern=traffic_pattern
    )
    return result


def run_policy_comparison(duration: float = 100.0,
                         traffic_rate: float = 3.0,
                         traffic_pattern: TrafficPattern = TrafficPattern.CONSTANT) -> List[Dict[str, Any]]:
    """Executa simulações comparando todas as políticas"""
    policies = [
        LoadBalancingPolicy.RANDOM,
        LoadBalancingPolicy.ROUND_ROBIN, 
        LoadBalancingPolicy.SHORTEST_QUEUE
    ]
    
    results = []
    analyzer = MetricsAnalyzer()
    
    print(f"\n🔄 INICIANDO COMPARAÇÃO DE POLÍTICAS")
    print(f"Duração por simulação: {duration}s")
    print(f"Taxa de tráfego: {traffic_rate} req/s")
    print(f"Padrão: {traffic_pattern.value}")
    print(f"Políticas a testar: {len(policies)}")
    
    for i, policy in enumerate(policies, 1):
        print(f"\n--- Executando simulação {i}/{len(policies)}: {policy.value} ---")
        
        result = run_single_simulation(
            duration=duration,
            traffic_rate=traffic_rate,
            policy=policy, 
            traffic_pattern=traffic_pattern
        )
        
        results.append(result)
        analyzer.add_simulation_result(result, f"Policy_{policy.value}")
        analyzer.print_summary(result)
    
    # Análise comparativa
    print(f"\n📋 ANÁLISE COMPARATIVA DAS POLÍTICAS")
    comparison = analyzer.compare_policies(results)
    
    print(f"\n🏆 MELHORES POLÍTICAS POR MÉTRICA:")
    for metric, best_policy in comparison["best_policy"].items():
        print(f"  • {metric}: {best_policy}")
    
    print(f"\n📊 RESUMO GERAL:")
    for policy, summary in comparison["summary"].items():
        print(f"\n  {policy.upper()}:")
        print(f"    Score geral: {summary['overall_score']}/100")
        if summary['strengths']:
            print(f"    Pontos fortes: {', '.join(summary['strengths'])}")
        if summary['weaknesses']:  
            print(f"    Pontos fracos: {', '.join(summary['weaknesses'])}")
        print(f"    Recomendado para: {summary['recommended_for']}")
    
    # Gera relatório
    analyzer.generate_report("policy_comparison_report.json")
    
    return results


def run_traffic_pattern_analysis(duration: float = 80.0,
                                traffic_rate: float = 2.5) -> List[Dict[str, Any]]:
    """Testa diferentes padrões de tráfego com a melhor política"""
    patterns = [TrafficPattern.CONSTANT, TrafficPattern.BURST]
    best_policy = LoadBalancingPolicy.SHORTEST_QUEUE  # Geralmente a melhor
    
    results = []
    analyzer = MetricsAnalyzer()
    
    print(f"\n🌊 ANÁLISE DE PADRÕES DE TRÁFEGO")
    print(f"Política utilizada: {best_policy.value}")
    print(f"Duração por simulação: {duration}s")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n--- Testando padrão {i}/{len(patterns)}: {pattern.value} ---")
        
        result = run_single_simulation(
            duration=duration,
            traffic_rate=traffic_rate,
            policy=best_policy,
            traffic_pattern=pattern
        )
        
        results.append(result)
        analyzer.add_simulation_result(result, f"Traffic_{pattern.value}")
        analyzer.print_summary(result)
    
    # Análise de padrões
    traffic_analysis = analyzer.analyze_traffic_patterns(results)
    
    print(f"\n📋 ANÁLISE DE PADRÕES DE TRÁFEGO:")
    for pattern, recommendation in traffic_analysis["recommendations"].items():
        print(f"  • {pattern}: {recommendation['reason']}")
    
    analyzer.generate_report("traffic_pattern_report.json")
    
    return results


def run_comprehensive_analysis():
    """Executa análise completa do sistema"""
    print(f"\n{'='*80}")
    print(f"🚀 SIMULADOR DE LOAD BALANCE - ANÁLISE COMPLETA")
    print(f"{'='*80}")
    
    all_results = []
    
    # 1. Comparação de políticas com tráfego constante
    print(f"\n\n1️⃣ FASE 1: COMPARAÇÃO DE POLÍTICAS (Tráfego Constante)")
    constant_results = run_policy_comparison(
        duration=120.0,
        traffic_rate=3.0, 
        traffic_pattern=TrafficPattern.CONSTANT
    )
    all_results.extend(constant_results)
    
    # 2. Comparação de políticas com tráfego em rajadas
    print(f"\n\n2️⃣ FASE 2: COMPARAÇÃO DE POLÍTICAS (Tráfego em Rajadas)")
    burst_results = run_policy_comparison(
        duration=120.0,
        traffic_rate=2.0,
        traffic_pattern=TrafficPattern.BURST
    )
    all_results.extend(burst_results)
    
    # 3. Análise de escalabilidade (teste com carga alta)
    print(f"\n\n3️⃣ FASE 3: TESTE DE ALTA CARGA")
    high_load_result = run_single_simulation(
        duration=100.0,
        traffic_rate=8.0,  # Alta carga
        policy=LoadBalancingPolicy.SHORTEST_QUEUE,
        traffic_pattern=TrafficPattern.BURST
    )
    all_results.append(high_load_result)
    
    # Análise final
    final_analyzer = MetricsAnalyzer()
    for result in all_results:
        final_analyzer.add_simulation_result(result)
    
    final_analyzer.generate_report("comprehensive_analysis_report.json")
    
    print(f"\n\n📋 CONCLUSÕES FINAIS:")
    print(f"✅ Total de simulações executadas: {len(all_results)}")
    print(f"✅ Políticas testadas: Random, Round Robin, Shortest Queue")
    print(f"✅ Padrões de tráfego testados: Constante, Rajadas")
    print(f"✅ Relatórios gerados em JSON para análise detalhada")
    
    print(f"\n💡 RECOMENDAÇÕES GERAIS:")
    print(f"• Shortest Queue: Melhor para otimização de latência e cargas heterogêneas")
    print(f"• Round Robin: Boa para distribuição equitativa em servidores homogêneos")
    print(f"• Random: Simples implementação, adequado para cargas uniformes")
    
    print(f"\n{'='*80}")
    print(f"🎉 ANÁLISE COMPLETA FINALIZADA!")
    print(f"{'='*80}")


def interactive_menu():
    """Menu interativo para o usuário"""
    while True:
        print(f"\n{'='*60}")
        print(f"🎮 SIMULADOR DE LOAD BALANCE - MENU PRINCIPAL")
        print(f"{'='*60}")
        print("1. Executar simulação única")
        print("2. Comparar todas as políticas")
        print("3. Analisar padrões de tráfego")
        print("4. Executar análise completa")
        print("5. Sair")
        print(f"{'='*60}")
        
        choice = input("Escolha uma opção (1-5): ").strip()
        
        if choice == "1":
            # Simulação única personalizada
            print("\n⚙️ CONFIGURAÇÃO DA SIMULAÇÃO")
            duration = float(input("Duração (segundos) [100]: ") or 100)
            rate = float(input("Taxa de requisições/s [3.0]: ") or 3.0)
            
            print("\nPolíticas disponíveis:")
            print("1. Random")
            print("2. Round Robin")  
            print("3. Shortest Queue")
            policy_choice = input("Escolha política (1-3) [2]: ").strip() or "2"
            
            policies_map = {
                "1": LoadBalancingPolicy.RANDOM,
                "2": LoadBalancingPolicy.ROUND_ROBIN,
                "3": LoadBalancingPolicy.SHORTEST_QUEUE
            }
            policy = policies_map.get(policy_choice, LoadBalancingPolicy.ROUND_ROBIN)
            
            print("\nPadrões de tráfego:")
            print("1. Constante")
            print("2. Rajadas")
            pattern_choice = input("Escolha padrão (1-2) [1]: ").strip() or "1"
            
            patterns_map = {
                "1": TrafficPattern.CONSTANT,
                "2": TrafficPattern.BURST
            }
            pattern = patterns_map.get(pattern_choice, TrafficPattern.CONSTANT)
            
            result = run_single_simulation(duration, rate, policy, pattern)
            analyzer = MetricsAnalyzer()
            analyzer.print_summary(result)
            
        elif choice == "2":
            duration = float(input("Duração por política (segundos) [100]: ") or 100)
            rate = float(input("Taxa de requisições/s [3.0]: ") or 3.0)
            run_policy_comparison(duration, rate)
            
        elif choice == "3":
            run_traffic_pattern_analysis()
            
        elif choice == "4":
            confirmation = input("Executar análise completa? Pode demorar alguns minutos (y/n): ")
            if confirmation.lower() in ['y', 'yes', 's', 'sim']:
                run_comprehensive_analysis()
            
        elif choice == "5":
            print("👋 Obrigado por usar o simulador!")
            break
            
        else:
            print("❌ Opção inválida!")
            
        input("\nPressione Enter para continuar...")


def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Modo linha de comando
        if sys.argv[1] == "--full-analysis":
            run_comprehensive_analysis()
        elif sys.argv[1] == "--compare-policies":
            run_policy_comparison()
        elif sys.argv[1] == "--traffic-analysis":
            run_traffic_pattern_analysis()
        else:
            print("Uso: python main.py [--full-analysis|--compare-policies|--traffic-analysis]")
    else:
        # Modo interativo
        interactive_menu()


if __name__ == "__main__":
    main()