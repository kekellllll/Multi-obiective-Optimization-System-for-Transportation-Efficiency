export interface Route {
  id: number;
  name: string;
  start_station: string;
  end_station: string;
  distance: number;
  estimated_travel_time: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Train {
  id: number;
  train_id: string;
  train_type: 'high_speed' | 'express' | 'local' | 'freight';
  capacity: number;
  max_speed: number;
  fuel_efficiency: number;
  maintenance_cost_per_km: string;
  is_operational: boolean;
  created_at: string;
  updated_at: string;
}

export interface Schedule {
  id: number;
  train: number;
  route: number;
  train_details?: Train;
  route_details?: Route;
  departure_time: string;
  arrival_time: string;
  passenger_load: number;
  is_cancelled: boolean;
  created_at: string;
  updated_at: string;
}

export interface OptimizationTask {
  id: number;
  task_id: string;
  user: number;
  user_name: string;
  optimization_type: 'schedule' | 'route' | 'fuel' | 'multi_objective';
  status: 'pending' | 'running' | 'completed' | 'failed';
  parameters: Record<string, any>;
  results: Record<string, any>;
  start_time?: string;
  end_time?: string;
  duration?: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface PerformanceMetric {
  id: number;
  metric_type: 'fuel_consumption' | 'on_time_performance' | 'passenger_satisfaction' | 'cost_efficiency' | 'route_utilization';
  value: number;
  unit: string;
  train?: number;
  route?: number;
  schedule?: number;
  train_details?: Train;
  route_details?: Route;
  measured_at: string;
  created_at: string;
}

export interface DashboardMetrics {
  total_trains: number;
  active_routes: number;
  scheduled_trips: number;
  avg_fuel_efficiency: number;
  on_time_performance: number;
  total_passengers: number;
  cost_savings: number;
  optimization_tasks_completed: number;
}

export interface OptimizationResult {
  objective_values: {
    fuel_consumption: number;
    on_time_performance: number;
    operational_costs: number;
    capacity_utilization: number;
  };
  optimal_schedules: Array<{
    train_id: string;
    route_name: string;
    departure_time: string;
    arrival_time: string;
    passenger_load: number;
    capacity_utilization: number;
  }>;
  performance_improvements: {
    estimated_fuel_savings: string;
    cost_reduction: string;
    efficiency_gain: string;
  };
  recommendations: string[];
}

export interface ApiResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface LoadingState {
  loading: boolean;
  error: string | null;
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>;
}