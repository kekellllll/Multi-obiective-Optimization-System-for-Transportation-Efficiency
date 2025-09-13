"""
Tests for DQN optimization functionality
"""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
# Mock numpy for tests if not available
try:
    import numpy as np
except ImportError:
    class MockNumpy:
        integer = int
        
        def array(self, data, dtype=None):
            return data
        
        def mean(self, data):
            return sum(data) / len(data) if data else 0
        
        def max(self, data):
            return max(data) if data else 0
        
        def zeros(self, size):
            return [0.0] * size
        
        def random(self):
            import random
            return random.random()
    
    import sys
    sys.modules['numpy'] = MockNumpy()
    np = MockNumpy()

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, patch

from train_optimization.dqn_optimization import (
    DQNAgent,
    DQNOptimizer,
    TransportationEnvironment
)
from train_optimization.models import OptimizationTask, Route, Train


class DQNEnvironmentTest(TestCase):
    """Test the DQN transportation environment"""

    def setUp(self):
        """Set up test data"""
        self.train = Train.objects.create(
            train_id="T001",
            train_type="express",
            capacity=200,
            max_speed=120.0,
            fuel_efficiency=12.5,
            maintenance_cost_per_km=2.50,
        )
        
        self.route = Route.objects.create(
            name="Main Line",
            start_station="Central",
            end_station="Airport",
            distance=45.0,
            estimated_travel_time=timedelta(hours=1),
        )

    def test_environment_initialization(self):
        """Test environment initialization"""
        env = TransportationEnvironment([self.train], [self.route])
        
        self.assertEqual(env.state_size, 12)
        self.assertEqual(env.action_size, 4)
        self.assertIn(self.train.id, env.train_states)
        self.assertIn(self.route.id, env.route_states)

    def test_environment_reset(self):
        """Test environment reset functionality"""
        env = TransportationEnvironment([self.train], [self.route])
        state = env.reset()
        
        self.assertEqual(len(state), env.state_size)
        # Check if all elements are numeric (allow for MockNumpy arrays)
        if hasattr(state, '__iter__'):
            self.assertTrue(all(isinstance(x, (int, float)) or str(x).replace('.', '').replace('-', '').isdigit() for x in state))
        self.assertEqual(env.total_fuel_consumed, 0.0)
        self.assertEqual(env.total_delays, 0)

    def test_environment_step(self):
        """Test environment step functionality"""
        env = TransportationEnvironment([self.train], [self.route])
        initial_state = env.reset()
        
        # Test each action
        for action in range(env.action_size):
            state, reward, done, info = env.step(action)
            
            self.assertEqual(len(state), env.state_size)
            self.assertIsInstance(reward, float)
            self.assertIsInstance(done, bool)
            self.assertIn('action_taken', info)


class DQNAgentTest(TestCase):
    """Test the DQN agent"""

    def test_agent_initialization(self):
        """Test DQN agent initialization"""
        agent = DQNAgent(state_size=12, action_size=4)
        
        self.assertEqual(agent.state_size, 12)
        self.assertEqual(agent.action_size, 4)
        self.assertEqual(agent.epsilon, 1.0)
        self.assertIsNotNone(agent.q_network)
        self.assertIsNotNone(agent.target_network)

    def test_agent_remember(self):
        """Test experience memory"""
        agent = DQNAgent(state_size=12, action_size=4)
        
        state = [0.5] * 12
        action = 1
        reward = 0.5
        next_state = [0.6] * 12
        done = False
        
        agent.remember(state, action, reward, next_state, done)
        
        self.assertEqual(len(agent.memory), 1)
        self.assertEqual(agent.memory[0][1], action)

    def test_agent_act(self):
        """Test action selection"""
        agent = DQNAgent(state_size=12, action_size=4)
        state = [0.5] * 12
        
        action = agent.act(state)
        
        self.assertIsInstance(action, (int, np.integer))
        self.assertGreaterEqual(action, 0)
        self.assertLess(action, agent.action_size)


class DQNOptimizerTest(TestCase):
    """Test the DQN optimizer"""

    def setUp(self):
        """Set up test data"""
        self.train = Train.objects.create(
            train_id="T001",
            train_type="express",
            capacity=200,
            max_speed=120.0,
            fuel_efficiency=12.5,
            maintenance_cost_per_km=2.50,
        )
        
        self.route = Route.objects.create(
            name="Main Line",
            start_station="Central",
            end_station="Airport",
            distance=45.0,
            estimated_travel_time=timedelta(hours=1),
        )

    def test_optimizer_initialization(self):
        """Test DQN optimizer initialization"""
        optimizer = DQNOptimizer()
        
        self.assertIsNone(optimizer.agent)
        self.assertIsNone(optimizer.environment)
        self.assertTrue(optimizer.model_path.endswith('.h5'))

    def test_optimize_with_no_data(self):
        """Test optimization with no trains or routes"""
        optimizer = DQNOptimizer()
        
        # Clear all data
        Train.objects.all().delete()
        Route.objects.all().delete()
        
        result = optimizer.optimize({})
        
        self.assertIn('error', result)
        self.assertIn('No available trains or routes', result['error'])

    def test_optimize_success(self):
        """Test successful DQN optimization"""
        optimizer = DQNOptimizer()
        
        # Use minimal parameters for faster test
        parameters = {
            "episodes": 2,
            "max_steps": 5
        }
        
        result = optimizer.optimize(parameters)
        
        # Check basic result structure
        self.assertIn('algorithm', result)
        self.assertEqual(result['algorithm'], 'Deep Q-Network (DQN)')
        self.assertIn('episodes_trained', result)
        self.assertIn('average_reward', result)
        self.assertIn('optimization_log', result)
        self.assertIn('recommendations', result)
        self.assertIn('performance_improvements', result)

    def test_predict_optimal_action(self):
        """Test optimal action prediction"""
        optimizer = DQNOptimizer()
        
        # Initialize with minimal setup
        optimizer.agent = DQNAgent(state_size=12, action_size=4)
        
        current_state = {
            "busy_ratio": 0.5,
            "avg_fuel": 0.8,
            "congestion_ratio": 0.3,
            "avg_delay": 5.0
        }
        
        result = optimizer.predict_optimal_action(current_state)
        
        self.assertIn('optimal_action', result)
        self.assertIn('action_code', result)
        self.assertIn('confidence', result)
        self.assertIn('state_evaluated', result)


class DQNIntegrationTest(APITestCase):
    """Integration tests for DQN with Django REST API"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        
        self.train = Train.objects.create(
            train_id="T001",
            train_type="express",
            capacity=200,
            max_speed=120.0,
            fuel_efficiency=12.5,
            maintenance_cost_per_km=2.50,
        )
        
        self.route = Route.objects.create(
            name="Main Line",
            start_station="Central",
            end_station="Airport",
            distance=45.0,
            estimated_travel_time=timedelta(hours=1),
        )

    @patch('train_optimization.views.run_optimization_task.delay')
    def test_create_dqn_optimization_task(self, mock_delay):
        """Test creating a DQN optimization task via API"""
        data = {
            "optimization_type": "dqn",
            "parameters": {
                "episodes": 2,
                "max_steps": 5
            }
        }
        
        response = self.client.post('/api/v1/optimization-tasks/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['optimization_type'], 'dqn')
        
        # Check task was created in database
        task = OptimizationTask.objects.get(optimization_type='dqn')
        self.assertEqual(task.optimization_type, 'dqn')
        self.assertEqual(task.status, 'pending')

    @patch('train_optimization.tasks.run_optimization_task.delay')
    def test_dqn_task_creation_triggers_celery(self, mock_delay):
        """Test that DQN task creation triggers Celery task"""
        with patch('train_optimization.views.run_optimization_task.delay') as mock_view_delay:
            data = {
                "optimization_type": "dqn",
                "parameters": {
                    "episodes": 2,
                    "max_steps": 5
                }
            }
            
            response = self.client.post('/api/v1/optimization-tasks/', data, format='json')
            
            self.assertEqual(response.status_code, 201)
            mock_view_delay.assert_called_once()
            
            # Check the arguments passed to Celery
            args, kwargs = mock_view_delay.call_args
            self.assertEqual(kwargs['optimization_type'], 'dqn')

    def test_list_optimization_types_includes_dqn(self):
        """Test that DQN is included in available optimization types"""
        from train_optimization.models import OptimizationTask
        
        optimization_types = dict(OptimizationTask.OPTIMIZATION_TYPE)
        
        self.assertIn('dqn', optimization_types)
        self.assertEqual(optimization_types['dqn'], 'Deep Q-Network (DQN)')

