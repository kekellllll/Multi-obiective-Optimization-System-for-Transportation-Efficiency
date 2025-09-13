import React from 'react';
import { Provider } from 'react-redux';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { store } from './store';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  color?: string;
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

const SimpleDashboard: React.FC = () => {
  // Mock data for demonstration
  const dashboardMetrics = {
    total_trains: 45,
    active_routes: 12,
    scheduled_trips: 234,
    cost_savings: 125000,
    avg_fuel_efficiency: 11.2,
    on_time_performance: 94.5,
    total_passengers: 15678,
    optimization_tasks_completed: 23
  };

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

      {/* Status Information */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Typography variant="body1" color="success.main">
                ✅ All systems operational
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last updated: {new Date().toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Multi-Objective Optimization
              </Typography>
              <Typography variant="body1">
                NSGA-II Algorithm Active
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Optimizing fuel efficiency, on-time performance, costs, and capacity utilization
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Multi-Objective Transportation Efficiency Optimization System
              </Typography>
            </Toolbar>
          </AppBar>
          <SimpleDashboard />
        </Box>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
