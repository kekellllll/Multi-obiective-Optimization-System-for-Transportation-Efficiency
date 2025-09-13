from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from train_optimization.models import Route, Train, Schedule, OptimizationTask
from datetime import datetime, timedelta


class RouteModelTest(TestCase):
    def setUp(self):
        self.route = Route.objects.create(
            name="Test Route",
            start_station="Station A",
            end_station="Station B",
            distance=100.0,
            estimated_travel_time=timedelta(hours=2)
        )

    def test_route_creation(self):
        self.assertEqual(self.route.name, "Test Route")
        self.assertEqual(self.route.start_station, "Station A")
        self.assertEqual(self.route.end_station, "Station B")
        self.assertEqual(self.route.distance, 100.0)
        self.assertTrue(self.route.is_active)

    def test_route_string_representation(self):
        expected = "Test Route: Station A → Station B"
        self.assertEqual(str(self.route), expected)


class TrainModelTest(TestCase):
    def setUp(self):
        self.train = Train.objects.create(
            train_id="TR001",
            train_type="express",
            capacity=200,
            max_speed=120.0,
            fuel_efficiency=10.5,
            maintenance_cost_per_km=5.00
        )

    def test_train_creation(self):
        self.assertEqual(self.train.train_id, "TR001")
        self.assertEqual(self.train.train_type, "express")
        self.assertEqual(self.train.capacity, 200)
        self.assertEqual(self.train.max_speed, 120.0)
        self.assertTrue(self.train.is_operational)

    def test_train_string_representation(self):
        expected = "TR001 (express)"
        self.assertEqual(str(self.train), expected)


class RouteAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.route = Route.objects.create(
            name="API Test Route",
            start_station="Station X",
            end_station="Station Y",
            distance=150.0,
            estimated_travel_time=timedelta(hours=3)
        )
        self.client.force_authenticate(user=self.user)

    def test_get_routes_list(self):
        url = reverse('route-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_route_detail(self):
        url = reverse('route-detail', kwargs={'pk': self.route.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "API Test Route")

    def test_create_route(self):
        url = reverse('route-list')
        data = {
            'name': 'New Route',
            'start_station': 'Station C',
            'end_station': 'Station D',
            'distance': 75.0,
            'estimated_travel_time': '01:30:00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 2)


class TrainAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.train = Train.objects.create(
            train_id="API001",
            train_type="local",
            capacity=150,
            max_speed=80.0,
            fuel_efficiency=12.0,
            maintenance_cost_per_km=4.50
        )
        self.client.force_authenticate(user=self.user)

    def test_get_trains_list(self):
        url = reverse('train-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_operational_trains(self):
        url = reverse('train-operational')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class OptimizationTaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.task = OptimizationTask.objects.create(
            task_id="test-task-123",
            user=self.user,
            optimization_type="multi_objective",
            parameters={"time_horizon": 24},
            status="pending"
        )

    def test_optimization_task_creation(self):
        self.assertEqual(self.task.task_id, "test-task-123")
        self.assertEqual(self.task.user, self.user)
        self.assertEqual(self.task.optimization_type, "multi_objective")
        self.assertEqual(self.task.status, "pending")

    def test_optimization_task_string_representation(self):
        expected = "Task test-task-123: multi_objective (pending)"
        self.assertEqual(str(self.task), expected)


class DashboardAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        # Create some test data
        self.train = Train.objects.create(
            train_id="DASH001",
            train_type="express",
            capacity=200,
            max_speed=120.0,
            fuel_efficiency=10.5,
            maintenance_cost_per_km=5.00
        )
        self.route = Route.objects.create(
            name="Dashboard Route",
            start_station="Station A",
            end_station="Station B",
            distance=100.0,
            estimated_travel_time=timedelta(hours=2)
        )
        self.client.force_authenticate(user=self.user)

    def test_dashboard_metrics(self):
        url = reverse('performancemetric-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that dashboard metrics contain expected fields
        expected_fields = [
            'total_trains', 'active_routes', 'scheduled_trips',
            'avg_fuel_efficiency', 'on_time_performance',
            'total_passengers', 'cost_savings', 'optimization_tasks_completed'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)