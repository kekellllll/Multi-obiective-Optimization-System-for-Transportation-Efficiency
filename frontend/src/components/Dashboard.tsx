import React, { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { fetchDashboardMetrics, fetchPerformanceTrends } from '../../store/slices/performanceSlice';
import { fetchUpcomingSchedules } from '../../store/slices/scheduleSlice';

interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  color?: string;
  icon?: React.ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, color = 'primary' }) => (
  <Card>
    <CardContent>
      <Typography variant="h6" color="textSecondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h4" color={color}>
        {typeof value === 'number' ? value.toLocaleString() : value}
        {unit && <Typography variant="body2" component="span" color="textSecondary">{' '}{unit}</Typography>}
      </Typography>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { dashboardMetrics, loading, error } = useAppSelector((state) => state.performance);
  const { upcomingSchedules } = useAppSelector((state) => state.schedules);
  
  const [trendData, setTrendData] = useState<any[]>([]);

  useEffect(() => {
    dispatch(fetchDashboardMetrics());
    dispatch(fetchUpcomingSchedules());
    dispatch(fetchPerformanceTrends({ type: 'fuel_consumption', days: 7 }))
      .then((result) => {
        if (result.payload) {
          setTrendData(result.payload.trends || []);
        }
      });

    // Set up real-time updates
    const interval = setInterval(() => {
      dispatch(fetchDashboardMetrics());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [dispatch]);

  if (loading && !dashboardMetrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!dashboardMetrics) {
    return null;
  }

  const performanceData = [
    { name: 'Fuel Efficiency', value: dashboardMetrics.avg_fuel_efficiency },
    { name: 'On-Time Performance', value: dashboardMetrics.on_time_performance },
    { name: 'Route Utilization', value: 85 }, // Simulated data
    { name: 'Cost Efficiency', value: 78 }, // Simulated data
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Transportation Optimization Dashboard
      </Typography>
      
      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Trains"
            value={dashboardMetrics.total_trains}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Routes"
            value={dashboardMetrics.active_routes}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Scheduled Trips"
            value={dashboardMetrics.scheduled_trips}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Cost Savings"
            value={`$${dashboardMetrics.cost_savings.toLocaleString()}`}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Fuel Efficiency"
            value={dashboardMetrics.avg_fuel_efficiency.toFixed(1)}
            unit="km/L"
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="On-Time Performance"
            value={`${dashboardMetrics.on_time_performance.toFixed(1)}%`}
            color={dashboardMetrics.on_time_performance >= 90 ? 'success' : 'warning'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Passengers"
            value={dashboardMetrics.total_passengers}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Optimization Tasks"
            value={dashboardMetrics.optimization_tasks_completed}
            color="secondary"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Fuel Consumption Trend */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fuel Consumption Trend (Last 7 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="average_value"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Fuel Consumption (L/100km)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={performanceData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {performanceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Schedules */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upcoming Schedules
              </Typography>
              {upcomingSchedules.length > 0 ? (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {upcomingSchedules.slice(0, 10).map((schedule) => (
                    <Chip
                      key={schedule.id}
                      label={`${schedule.train_details?.train_id || 'Train'} - ${schedule.route_details?.name || 'Route'} at ${new Date(schedule.departure_time).toLocaleTimeString()}`}
                      variant="outlined"
                      color="primary"
                      size="small"
                    />
                  ))}
                </Box>
              ) : (
                <Typography color="textSecondary">
                  No upcoming schedules
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Train Type Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fleet Composition
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart
                  data={[
                    { type: 'High Speed', count: Math.floor(dashboardMetrics.total_trains * 0.3) },
                    { type: 'Express', count: Math.floor(dashboardMetrics.total_trains * 0.4) },
                    { type: 'Local', count: Math.floor(dashboardMetrics.total_trains * 0.2) },
                    { type: 'Freight', count: Math.floor(dashboardMetrics.total_trains * 0.1) },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Efficiency Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Efficiency Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart
                  data={[
                    { metric: 'Fuel Efficiency', current: dashboardMetrics.avg_fuel_efficiency, target: 12 },
                    { metric: 'On-Time %', current: dashboardMetrics.on_time_performance, target: 95 },
                    { metric: 'Capacity Util.', current: 75, target: 85 },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="current" fill="#8884d8" name="Current" />
                  <Bar dataKey="target" fill="#82ca9d" name="Target" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;