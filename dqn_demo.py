#!/usr/bin/env python3
"""
DQN (Deep Q-Network) 使用示例脚本

这个脚本演示了如何在交通运输优化系统中使用 DQN 进行实时决策优化。
"""

import os
import sys
import django
from datetime import timedelta

# 设置 Django 环境
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transportation_optimization_backend.settings')
django.setup()

from train_optimization.dqn_optimization import DQNOptimizer, DQNAgent, TransportationEnvironment
from train_optimization.models import Train, Route, OptimizationTask
from django.contrib.auth.models import User


def create_sample_data():
    """创建示例数据"""
    print("📊 创建示例数据...")
    
    # 创建列车数据
    trains = [
        {
            'train_id': 'EXPRESS_001',
            'train_type': 'express', 
            'capacity': 300,
            'max_speed': 160.0,
            'fuel_efficiency': 15.2,
            'maintenance_cost_per_km': 3.50
        },
        {
            'train_id': 'LOCAL_002',
            'train_type': 'local',
            'capacity': 150,
            'max_speed': 80.0, 
            'fuel_efficiency': 18.5,
            'maintenance_cost_per_km': 2.20
        },
        {
            'train_id': 'HIGH_SPEED_003',
            'train_type': 'high_speed',
            'capacity': 400,
            'max_speed': 200.0,
            'fuel_efficiency': 12.8,
            'maintenance_cost_per_km': 5.00
        }
    ]
    
    created_trains = []
    for train_data in trains:
        train, created = Train.objects.get_or_create(
            train_id=train_data['train_id'],
            defaults={**train_data, 'is_operational': True}
        )
        created_trains.append(train)
        print(f"   ✅ 列车 {train.train_id} ({'创建' if created else '已存在'})")
    
    # 创建路线数据
    routes = [
        {
            'name': '主干线',
            'start_station': '中央车站',
            'end_station': '机场站',
            'distance': 45.0,
            'estimated_travel_time': timedelta(hours=1, minutes=10)
        },
        {
            'name': '市区环线',
            'start_station': '市中心',
            'end_station': '商业区',
            'distance': 25.0,
            'estimated_travel_time': timedelta(minutes=35)
        },
        {
            'name': '高速专线',
            'start_station': '北站',
            'end_station': '南站',
            'distance': 120.0,
            'estimated_travel_time': timedelta(hours=1, minutes=30)
        }
    ]
    
    created_routes = []
    for route_data in routes:
        route, created = Route.objects.get_or_create(
            name=route_data['name'],
            defaults={**route_data, 'is_active': True}
        )
        created_routes.append(route)
        print(f"   ✅ 路线 {route.name} ({'创建' if created else '已存在'})")
    
    return created_trains, created_routes


def demonstrate_dqn_environment():
    """演示 DQN 环境功能"""
    print("\n🤖 DQN 环境演示")
    
    trains = Train.objects.filter(is_operational=True)[:3]
    routes = Route.objects.filter(is_active=True)[:3]
    
    # 创建环境
    env = TransportationEnvironment(list(trains), list(routes))
    print(f"   状态空间维度: {env.state_size}")
    print(f"   动作空间大小: {env.action_size}")
    
    # 重置环境
    state = env.reset()
    print(f"   初始状态: {[f'{x:.3f}' for x in state[:6]]}...")
    
    # 演示几个动作
    actions = ['调度列车', '延误发车', '改变路线', '优化速度']
    
    for i, action_name in enumerate(actions):
        next_state, reward, done, info = env.step(i)
        print(f"   执行 '{action_name}': 奖励={reward:.3f}, 完成={done}")
        
    return env


def demonstrate_dqn_agent():
    """演示 DQN 智能体功能"""
    print("\n🧠 DQN 智能体演示")
    
    # 创建智能体
    agent = DQNAgent(state_size=12, action_size=4, learning_rate=0.001)
    print(f"   智能体参数:")
    print(f"     学习率: {agent.learning_rate}")
    print(f"     探索率: {agent.epsilon}")
    print(f"     批次大小: {agent.batch_size}")
    
    # 测试决策
    test_state = [0.5, 0.8, 0.3, 5.0, 0.5, 0.4, 0.7, 0.8, 0.6, 0.4, 0.3, 0.5]
    action = agent.act(test_state)
    action_names = {0: "调度列车", 1: "延误发车", 2: "改变路线", 3: "优化速度"}
    print(f"   测试状态下选择的动作: {action_names[action]}")
    
    return agent


def demonstrate_dqn_optimization():
    """演示完整的 DQN 优化过程"""
    print("\n🎯 DQN 优化演示")
    
    # 创建优化器
    optimizer = DQNOptimizer()
    
    # 设置训练参数
    parameters = {
        'episodes': 10,          # 训练轮数
        'max_steps': 50,         # 每轮最大步数
        'learning_rate': 0.001   # 学习率
    }
    
    print("   开始 DQN 训练优化...")
    print(f"   参数: {parameters}")
    
    # 执行优化
    results = optimizer.optimize(parameters)
    
    # 显示结果
    print("\n📈 优化结果:")
    print(f"   算法: {results.get('algorithm', 'Unknown')}")
    print(f"   训练轮数: {results.get('episodes_trained', 0)}")
    print(f"   平均奖励: {results.get('average_reward', 0):.3f}")
    print(f"   最终探索率: {results.get('final_epsilon', 0):.3f}")
    print(f"   模型已保存: {results.get('model_saved', False)}")
    
    print("\n🎯 性能改进预测:")
    improvements = results.get('performance_improvements', {})
    for metric, value in improvements.items():
        metric_names = {
            'fuel_efficiency_gain': '燃油效率提升',
            'schedule_optimization': '调度优化改进', 
            'route_utilization': '路线利用率提高',
            'delay_reduction': '延误减少'
        }
        print(f"   {metric_names.get(metric, metric)}: {value}")
    
    print("\n💡 系统建议:")
    recommendations = results.get('recommendations', [])
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    return results


def demonstrate_real_time_prediction():
    """演示实时决策预测"""
    print("\n⚡ 实时决策预测演示")
    
    optimizer = DQNOptimizer()
    
    # 模拟当前系统状态
    current_states = [
        {
            "scenario": "高峰时段",
            "state": {
                "busy_ratio": 0.8,      # 80% 列车在运行
                "avg_fuel": 0.6,        # 60% 燃油水平
                "congestion_ratio": 0.7, # 70% 路线拥堵
                "avg_delay": 8.0,       # 平均延误 8 分钟
                "fuel_efficiency": 0.65,
                "delay_penalty": 0.7,
                "passenger_load": 0.9,
                "fleet_size": 25,
                "network_size": 15
            }
        },
        {
            "scenario": "低峰时段", 
            "state": {
                "busy_ratio": 0.3,      # 30% 列车在运行
                "avg_fuel": 0.9,        # 90% 燃油水平
                "congestion_ratio": 0.1, # 10% 路线拥堵
                "avg_delay": 2.0,       # 平均延误 2 分钟
                "fuel_efficiency": 0.85,
                "delay_penalty": 0.95,
                "passenger_load": 0.4,
                "fleet_size": 25,
                "network_size": 15
            }
        }
    ]
    
    # 为每个场景预测最优动作
    for scenario_data in current_states:
        scenario = scenario_data["scenario"]
        state = scenario_data["state"]
        
        print(f"\n   场景: {scenario}")
        print(f"   当前状态: 忙碌率={state['busy_ratio']:.1%}, "
              f"拥堵率={state['congestion_ratio']:.1%}, "
              f"平均延误={state['avg_delay']:.1f}分钟")
        
        # 需要先初始化智能体
        optimizer.agent = DQNAgent(state_size=12, action_size=4)
        
        prediction = optimizer.predict_optimal_action(state)
        
        action_descriptions = {
            "schedule_train": "调度新列车 - 增加运力应对需求",
            "delay_departure": "延误发车 - 优化时刻表间隔",
            "change_route": "改变路线 - 避开拥堵路段",
            "optimize_speed": "优化速度 - 提高燃油效率"
        }
        
        optimal_action = prediction.get('optimal_action', 'unknown')
        confidence = prediction.get('confidence', 0)
        
        print(f"   🎯 推荐动作: {action_descriptions.get(optimal_action, optimal_action)}")
        print(f"   📊 置信度: {confidence:.1%}")


def main():
    """主函数"""
    print("🚄 DQN 交通运输优化系统演示")
    print("=" * 50)
    
    try:
        # 1. 创建示例数据
        trains, routes = create_sample_data()
        
        # 2. 演示 DQN 环境
        env = demonstrate_dqn_environment()
        
        # 3. 演示 DQN 智能体
        agent = demonstrate_dqn_agent()
        
        # 4. 演示完整优化
        results = demonstrate_dqn_optimization()
        
        # 5. 演示实时决策
        demonstrate_real_time_prediction()
        
        print("\n" + "=" * 50)
        print("✅ DQN 系统演示完成！")
        print("\n📋 总结:")
        print("   - DQN 能够处理复杂的实时交通调度问题")
        print("   - 通过强化学习自动优化多个目标")
        print("   - 适应动态变化的交通环境")
        print("   - 提供实时决策支持")
        print("\n🔗 更多信息请查看 DQN_USAGE_ANALYSIS.md")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()