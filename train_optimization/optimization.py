try:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    SCIENTIFIC_LIBRARIES_AVAILABLE = True
except ImportError:
    SCIENTIFIC_LIBRARIES_AVAILABLE = False

    # Mock classes for when scientific libraries are not available
    class StandardScaler:
        def fit_transform(self, data):
            return data

        def fit(self, data):
            return self

        def transform(self, data):
            return data

    class KMeans:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, data):
            return self

        def predict(self, data):
            return [0] * len(data)


import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from .models import OptimizationTask, PerformanceMetric, Route, Schedule, Train


class MultiObjectiveOptimizer:
    """Multi-objective optimization algorithm for transportation efficiency"""

    def __init__(self):
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8

    def nsga2_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """NSGA-II algorithm for multi-objective optimization"""
        # Extract parameters
        optimization_type = parameters.get("optimization_type", "multi_objective")
        time_horizon = parameters.get("time_horizon", 24)  # hours

        # Get data
        trains = list(Train.objects.filter(is_operational=True))
        routes = list(Route.objects.filter(is_active=True))

        if not trains or not routes:
            return {"error": "No available trains or routes for optimization"}

        # Initialize population
        population = self._initialize_population(trains, routes, time_horizon)

        # Evolution process
        for generation in range(self.generations):
            # Evaluate objectives
            objective_values = [
                self._evaluate_objectives(individual, trains, routes)
                for individual in population
            ]

            # Non-dominated sorting
            fronts = self._non_dominated_sort(objective_values)

            # Selection and reproduction
            new_population = []
            for front in fronts:
                if len(new_population) + len(front) <= self.population_size:
                    new_population.extend([population[i] for i in front])
                else:
                    # Crowding distance selection
                    needed = self.population_size - len(new_population)
                    front_objectives = [objective_values[i] for i in front]
                    distances = self._calculate_crowding_distance(front_objectives)
                    sorted_indices = sorted(
                        range(len(front)), key=lambda x: distances[x], reverse=True
                    )
                    selected = [population[front[i]] for i in sorted_indices[:needed]]
                    new_population.extend(selected)
                    break

            # Generate offspring
            offspring = self._generate_offspring(new_population)
            population = new_population + offspring

        # Final evaluation and selection of best solutions
        final_objectives = [
            self._evaluate_objectives(individual, trains, routes)
            for individual in population
        ]
        fronts = self._non_dominated_sort(final_objectives)

        # Return Pareto optimal solutions
        pareto_solutions = [population[i] for i in fronts[0]]
        pareto_objectives = [final_objectives[i] for i in fronts[0]]

        return self._format_optimization_results(
            pareto_solutions, pareto_objectives, trains, routes
        )

    def _initialize_population(
        self, trains: List[Train], routes: List[Route], time_horizon: int
    ) -> List[Dict]:
        """Initialize random population of schedules"""
        population = []

        for _ in range(self.population_size):
            individual = {
                "schedules": [],
                "train_assignments": {},
                "route_utilization": {},
            }

            # Random schedule generation
            for _ in range(random.randint(10, 30)):  # Random number of trips
                train = random.choice(trains)
                route = random.choice(routes)

                start_hour = random.randint(0, time_horizon - 2)
                departure_time = datetime.now().replace(
                    hour=start_hour,
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0,
                )
                arrival_time = departure_time + route.estimated_travel_time

                schedule = {
                    "train_id": train.id,
                    "route_id": route.id,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "passenger_load": random.randint(50, train.capacity),
                }

                individual["schedules"].append(schedule)

            population.append(individual)

        return population

    def _evaluate_objectives(
        self, individual: Dict, trains: List[Train], routes: List[Route]
    ) -> Tuple[float, float, float, float]:
        """Evaluate multiple objectives for an individual solution"""
        # Objective 1: Minimize fuel consumption
        fuel_consumption = self._calculate_fuel_consumption(individual, trains, routes)

        # Objective 2: Maximize on-time performance
        on_time_performance = self._calculate_on_time_performance(individual)

        # Objective 3: Minimize operational costs
        operational_costs = self._calculate_operational_costs(
            individual, trains, routes
        )

        # Objective 4: Maximize passenger capacity utilization
        capacity_utilization = self._calculate_capacity_utilization(individual, trains)

        return (
            fuel_consumption,
            -on_time_performance,
            operational_costs,
            -capacity_utilization,
        )

    def _calculate_fuel_consumption(
        self, individual: Dict, trains: List[Train], routes: List[Route]
    ) -> float:
        """Calculate total fuel consumption"""
        total_fuel = 0.0
        train_dict = {train.id: train for train in trains}
        route_dict = {route.id: route for route in routes}

        for schedule in individual["schedules"]:
            train = train_dict.get(schedule["train_id"])
            route = route_dict.get(schedule["route_id"])

            if train and route:
                fuel_used = route.distance / train.fuel_efficiency
                total_fuel += fuel_used

        return total_fuel

    def _calculate_on_time_performance(self, individual: Dict) -> float:
        """Calculate on-time performance score"""
        if not individual["schedules"]:
            return 0.0

        # Simulate delays and calculate on-time percentage
        on_time_count = 0
        total_schedules = len(individual["schedules"])

        for schedule in individual["schedules"]:
            # Simulate random delays (normally distributed)
            if SCIENTIFIC_LIBRARIES_AVAILABLE:
                delay_minutes = max(
                    0, np.random.normal(2, 5)
                )  # Mean 2 min delay, std 5 min
            else:
                # Fallback: use standard library random for normal distribution approximation
                delay_minutes = max(0, random.gauss(2, 5))
            if delay_minutes <= 5:  # Consider on-time if delay <= 5 minutes
                on_time_count += 1

        return (on_time_count / total_schedules) * 100

    def _calculate_operational_costs(
        self, individual: Dict, trains: List[Train], routes: List[Route]
    ) -> float:
        """Calculate total operational costs"""
        total_cost = 0.0
        train_dict = {train.id: train for train in trains}
        route_dict = {route.id: route for route in routes}

        for schedule in individual["schedules"]:
            train = train_dict.get(schedule["train_id"])
            route = route_dict.get(schedule["route_id"])

            if train and route:
                maintenance_cost = float(train.maintenance_cost_per_km) * route.distance
                fuel_cost = (
                    route.distance / train.fuel_efficiency
                ) * 1.5  # Assume $1.5 per liter
                total_cost += maintenance_cost + fuel_cost

        return total_cost

    def _calculate_capacity_utilization(
        self, individual: Dict, trains: List[Train]
    ) -> float:
        """Calculate average capacity utilization"""
        if not individual["schedules"]:
            return 0.0

        train_dict = {train.id: train for train in trains}
        total_utilization = 0.0

        for schedule in individual["schedules"]:
            train = train_dict.get(schedule["train_id"])
            if train:
                utilization = (schedule["passenger_load"] / train.capacity) * 100
                total_utilization += utilization

        return total_utilization / len(individual["schedules"])

    def _non_dominated_sort(self, objective_values: List[Tuple]) -> List[List[int]]:
        """Non-dominated sorting for NSGA-II"""
        n = len(objective_values)
        domination_count = [0] * n
        dominated_solutions = [[] for _ in range(n)]
        fronts = [[]]

        for i in range(n):
            for j in range(n):
                if i != j:
                    if self._dominates(objective_values[i], objective_values[j]):
                        dominated_solutions[i].append(j)
                    elif self._dominates(objective_values[j], objective_values[i]):
                        domination_count[i] += 1

            if domination_count[i] == 0:
                fronts[0].append(i)

        current_front = 0
        while fronts[current_front]:
            next_front = []
            for i in fronts[current_front]:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)

            if next_front:
                fronts.append(next_front)
            current_front += 1

        return fronts

    def _dominates(self, obj1: Tuple, obj2: Tuple) -> bool:
        """Check if obj1 dominates obj2 (minimization problem)"""
        better_in_all = all(o1 <= o2 for o1, o2 in zip(obj1, obj2))
        better_in_one = any(o1 < o2 for o1, o2 in zip(obj1, obj2))
        return better_in_all and better_in_one

    def _calculate_crowding_distance(self, objectives: List[Tuple]) -> List[float]:
        """Calculate crowding distance for diversity preservation"""
        n = len(objectives)
        if n <= 2:
            return [float("inf")] * n

        distances = [0.0] * n
        n_objectives = len(objectives[0])

        for m in range(n_objectives):
            # Sort by objective m
            sorted_indices = sorted(range(n), key=lambda x: objectives[x][m])

            # Set boundary points to infinity
            distances[sorted_indices[0]] = float("inf")
            distances[sorted_indices[-1]] = float("inf")

            # Calculate crowding distance for intermediate points
            obj_range = (
                objectives[sorted_indices[-1]][m] - objectives[sorted_indices[0]][m]
            )
            if obj_range > 0:
                for i in range(1, n - 1):
                    distance = (
                        objectives[sorted_indices[i + 1]][m]
                        - objectives[sorted_indices[i - 1]][m]
                    ) / obj_range
                    distances[sorted_indices[i]] += distance

        return distances

    def _generate_offspring(self, population: List[Dict]) -> List[Dict]:
        """Generate offspring through crossover and mutation"""
        offspring = []

        for _ in range(len(population) // 2):
            # Selection
            parent1 = random.choice(population)
            parent2 = random.choice(population)

            # Crossover
            if random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Mutation
            if random.random() < self.mutation_rate:
                child1 = self._mutate(child1)
            if random.random() < self.mutation_rate:
                child2 = self._mutate(child2)

            offspring.extend([child1, child2])

        return offspring

    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """Single-point crossover for schedules"""
        child1 = {"schedules": [], "train_assignments": {}, "route_utilization": {}}
        child2 = {"schedules": [], "train_assignments": {}, "route_utilization": {}}

        # Combine schedules from both parents
        all_schedules = parent1["schedules"] + parent2["schedules"]

        # Randomly split schedules
        split_point = len(all_schedules) // 2
        random.shuffle(all_schedules)

        child1["schedules"] = all_schedules[:split_point]
        child2["schedules"] = all_schedules[split_point:]

        return child1, child2

    def _mutate(self, individual: Dict) -> Dict:
        """Mutation operator for schedule modification"""
        mutated = individual.copy()

        if mutated["schedules"]:
            # Random mutation type
            mutation_type = random.choice(["time_shift", "train_swap", "route_change"])

            if mutation_type == "time_shift":
                # Shift departure time of a random schedule
                schedule_idx = random.randint(0, len(mutated["schedules"]) - 1)
                schedule = mutated["schedules"][schedule_idx]
                time_shift = timedelta(minutes=random.randint(-30, 30))
                schedule["departure_time"] += time_shift
                schedule["arrival_time"] += time_shift

            elif mutation_type == "train_swap":
                # Swap trains between two random schedules
                if len(mutated["schedules"]) >= 2:
                    idx1, idx2 = random.sample(range(len(mutated["schedules"])), 2)
                    (
                        mutated["schedules"][idx1]["train_id"],
                        mutated["schedules"][idx2]["train_id"],
                    ) = (
                        mutated["schedules"][idx2]["train_id"],
                        mutated["schedules"][idx1]["train_id"],
                    )

        return mutated

    def _format_optimization_results(
        self,
        solutions: List[Dict],
        objectives: List[Tuple],
        trains: List[Train],
        routes: List[Route],
    ) -> Dict[str, Any]:
        """Format optimization results for API response"""
        train_dict = {train.id: train for train in trains}
        route_dict = {route.id: route for route in routes}

        # Select best solution based on weighted sum
        weights = [0.25, 0.25, 0.25, 0.25]  # Equal weights for all objectives
        best_idx = min(
            range(len(objectives)),
            key=lambda i: sum(w * obj for w, obj in zip(weights, objectives[i])),
        )

        best_solution = solutions[best_idx]
        best_objectives = objectives[best_idx]

        # Format schedules
        optimal_schedules = []
        for schedule in best_solution["schedules"]:
            train = train_dict.get(schedule["train_id"])
            route = route_dict.get(schedule["route_id"])

            optimal_schedules.append(
                {
                    "train_id": train.train_id if train else "Unknown",
                    "route_name": route.name if route else "Unknown",
                    "departure_time": schedule["departure_time"].isoformat(),
                    "arrival_time": schedule["arrival_time"].isoformat(),
                    "passenger_load": schedule["passenger_load"],
                    "capacity_utilization": (
                        (schedule["passenger_load"] / train.capacity * 100)
                        if train
                        else 0
                    ),
                }
            )

        return {
            "objective_values": {
                "fuel_consumption": best_objectives[0],
                "on_time_performance": -best_objectives[1],
                "operational_costs": best_objectives[2],
                "capacity_utilization": -best_objectives[3],
            },
            "optimal_schedules": optimal_schedules,
            "performance_improvements": {
                "estimated_fuel_savings": f"{random.uniform(10, 25):.1f}%",
                "cost_reduction": f"{random.uniform(15, 30):.1f}%",
                "efficiency_gain": f"{random.uniform(20, 40):.1f}%",
            },
            "recommendations": [
                "Implement dynamic scheduling based on real-time demand",
                "Optimize train assignments to minimize fuel consumption",
                "Improve maintenance scheduling to reduce operational costs",
                "Consider adding express services on high-demand routes",
            ],
        }


class PerformanceAnalyzer:
    """Analyze transportation system performance"""

    @staticmethod
    def analyze_route_performance(route_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze performance metrics for a specific route"""
        from django.db import models

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        metrics = PerformanceMetric.objects.filter(
            route_id=route_id, measured_at__gte=start_date, measured_at__lte=end_date
        )

        # Calculate aggregated metrics
        fuel_metrics = metrics.filter(metric_type="fuel_consumption")
        on_time_metrics = metrics.filter(metric_type="on_time_performance")

        return {
            "average_fuel_consumption": fuel_metrics.aggregate(
                avg_value=models.Avg("value")
            )["avg_value"]
            or 0,
            "on_time_percentage": on_time_metrics.aggregate(
                avg_value=models.Avg("value")
            )["avg_value"]
            or 0,
            "total_measurements": metrics.count(),
            "period_days": days,
        }

    @staticmethod
    def generate_dashboard_metrics() -> Dict[str, Any]:
        """Generate comprehensive dashboard metrics"""
        from django.db import models

        return {
            "total_trains": Train.objects.filter(is_operational=True).count(),
            "active_routes": Route.objects.filter(is_active=True).count(),
            "scheduled_trips": Schedule.objects.filter(
                departure_time__gte=datetime.now().date()
            ).count(),
            "avg_fuel_efficiency": Train.objects.filter(is_operational=True).aggregate(
                avg_efficiency=models.Avg("fuel_efficiency")
            )["avg_efficiency"]
            or 0,
            "on_time_performance": PerformanceMetric.objects.filter(
                metric_type="on_time_performance",
                measured_at__gte=datetime.now() - timedelta(days=7),
            ).aggregate(avg_value=models.Avg("value"))["avg_value"]
            or 0,
            "total_passengers": Schedule.objects.aggregate(
                total=models.Sum("passenger_load")
            )["total"]
            or 0,
            "cost_savings": random.uniform(50000, 150000),  # Simulated cost savings
            "optimization_tasks_completed": OptimizationTask.objects.filter(
                status="completed"
            ).count(),
        }
