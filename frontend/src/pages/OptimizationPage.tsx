import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import {
  fetchOptimizationTasks,
  createOptimizationTask,
  restartOptimizationTask,
  fetchMyTasks,
} from '../../store/slices/optimizationSlice';

const OptimizationPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { tasks, myTasks, loading, isCreating, error } = useAppSelector(
    (state) => state.optimization
  );

  const [open, setOpen] = useState(false);
  const [optimizationType, setOptimizationType] = useState('multi_objective');
  const [parameters, setParameters] = useState({
    time_horizon: 24,
    objective_weights: {
      fuel_efficiency: 0.25,
      on_time_performance: 0.25,
      cost_optimization: 0.25,
      capacity_utilization: 0.25,
    },
    constraints: {
      max_delay_minutes: 15,
      min_capacity_utilization: 60,
    },
  });

  useEffect(() => {
    dispatch(fetchMyTasks());
    dispatch(fetchOptimizationTasks());

    // Set up polling for task status updates
    const interval = setInterval(() => {
      dispatch(fetchMyTasks());
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [dispatch]);

  const handleCreate = async () => {
    try {
      await dispatch(
        createOptimizationTask({
          optimization_type: optimizationType,
          parameters,
        })
      ).unwrap();
      setOpen(false);
      setParameters({
        time_horizon: 24,
        objective_weights: {
          fuel_efficiency: 0.25,
          on_time_performance: 0.25,
          cost_optimization: 0.25,
          capacity_utilization: 0.25,
        },
        constraints: {
          max_delay_minutes: 15,
          min_capacity_utilization: 60,
        },
      });
    } catch (error) {
      console.error('Failed to create optimization task:', error);
    }
  };

  const handleRestart = (taskId: number) => {
    dispatch(restartOptimizationTask(taskId));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const renderOptimizationResults = (task: any) => {
    if (!task.results || Object.keys(task.results).length === 0) {
      return <Typography color="textSecondary">No results available</Typography>;
    }

    const { objective_values, optimal_schedules, performance_improvements, recommendations } = task.results;

    return (
      <Box>
        {objective_values && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Objective Values
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      Fuel Consumption
                    </Typography>
                    <Typography variant="h6">
                      {objective_values.fuel_consumption?.toFixed(2)} L
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      On-Time Performance
                    </Typography>
                    <Typography variant="h6">
                      {objective_values.on_time_performance?.toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      Operational Costs
                    </Typography>
                    <Typography variant="h6">
                      ${objective_values.operational_costs?.toFixed(0)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 1 }}>
                    <Typography variant="body2" color="textSecondary">
                      Capacity Utilization
                    </Typography>
                    <Typography variant="h6">
                      {objective_values.capacity_utilization?.toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {performance_improvements && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Performance Improvements
            </Typography>
            <Grid container spacing={1}>
              <Grid item>
                <Chip
                  label={`Fuel Savings: ${performance_improvements.estimated_fuel_savings}`}
                  color="success"
                  variant="outlined"
                />
              </Grid>
              <Grid item>
                <Chip
                  label={`Cost Reduction: ${performance_improvements.cost_reduction}`}
                  color="info"
                  variant="outlined"
                />
              </Grid>
              <Grid item>
                <Chip
                  label={`Efficiency Gain: ${performance_improvements.efficiency_gain}`}
                  color="warning"
                  variant="outlined"
                />
              </Grid>
            </Grid>
          </Box>
        )}

        {recommendations && recommendations.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            <ul>
              {recommendations.map((rec: string, index: number) => (
                <li key={index}>
                  <Typography variant="body2">{rec}</Typography>
                </li>
              ))}
            </ul>
          </Box>
        )}

        {optimal_schedules && optimal_schedules.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">
                Optimal Schedules ({optimal_schedules.length} schedules)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Train</TableCell>
                      <TableCell>Route</TableCell>
                      <TableCell>Departure</TableCell>
                      <TableCell>Arrival</TableCell>
                      <TableCell>Passengers</TableCell>
                      <TableCell>Utilization</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {optimal_schedules.slice(0, 10).map((schedule: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{schedule.train_id}</TableCell>
                        <TableCell>{schedule.route_name}</TableCell>
                        <TableCell>
                          {new Date(schedule.departure_time).toLocaleTimeString()}
                        </TableCell>
                        <TableCell>
                          {new Date(schedule.arrival_time).toLocaleTimeString()}
                        </TableCell>
                        <TableCell>{schedule.passenger_load}</TableCell>
                        <TableCell>{schedule.capacity_utilization?.toFixed(1)}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Multi-Objective Optimization
        </Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={() => dispatch(fetchMyTasks())}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
            disabled={isCreating}
          >
            New Optimization
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* My Optimization Tasks */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            My Optimization Tasks
          </Typography>
          {loading ? (
            <LinearProgress />
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Task ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {myTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>{task.task_id.substring(0, 8)}...</TableCell>
                      <TableCell>
                        <Chip
                          label={task.optimization_type.replace('_', ' ')}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={task.status}
                          color={getStatusColor(task.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(task.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {task.duration
                          ? `${(task.duration / 1000).toFixed(1)}s`
                          : task.status === 'running'
                          ? 'Running...'
                          : '-'}
                      </TableCell>
                      <TableCell>
                        {task.status === 'failed' && (
                          <Button
                            size="small"
                            startIcon={<PlayArrowIcon />}
                            onClick={() => handleRestart(task.id)}
                          >
                            Restart
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {myTasks.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No optimization tasks found
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Task Results */}
      {myTasks
        .filter((task) => task.status === 'completed' && task.results)
        .map((task) => (
          <Card key={task.id} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Results for Task {task.task_id.substring(0, 8)}...
                <Chip
                  label={task.optimization_type.replace('_', ' ')}
                  size="small"
                  sx={{ ml: 1 }}
                />
              </Typography>
              {renderOptimizationResults(task)}
            </CardContent>
          </Card>
        ))}

      {/* Create Optimization Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Optimization Task</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Optimization Type</InputLabel>
                <Select
                  value={optimizationType}
                  onChange={(e) => setOptimizationType(e.target.value)}
                  label="Optimization Type"
                >
                  <MenuItem value="multi_objective">Multi-Objective</MenuItem>
                  <MenuItem value="schedule">Schedule Optimization</MenuItem>
                  <MenuItem value="route">Route Optimization</MenuItem>
                  <MenuItem value="fuel">Fuel Efficiency</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Time Horizon (hours)"
                type="number"
                value={parameters.time_horizon}
                onChange={(e) =>
                  setParameters({
                    ...parameters,
                    time_horizon: parseInt(e.target.value),
                  })
                }
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Objective Weights
              </Typography>
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Fuel Efficiency"
                type="number"
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                value={parameters.objective_weights.fuel_efficiency}
                onChange={(e) =>
                  setParameters({
                    ...parameters,
                    objective_weights: {
                      ...parameters.objective_weights,
                      fuel_efficiency: parseFloat(e.target.value),
                    },
                  })
                }
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                label="On-Time Performance"
                type="number"
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                value={parameters.objective_weights.on_time_performance}
                onChange={(e) =>
                  setParameters({
                    ...parameters,
                    objective_weights: {
                      ...parameters.objective_weights,
                      on_time_performance: parseFloat(e.target.value),
                    },
                  })
                }
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Cost Optimization"
                type="number"
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                value={parameters.objective_weights.cost_optimization}
                onChange={(e) =>
                  setParameters({
                    ...parameters,
                    objective_weights: {
                      ...parameters.objective_weights,
                      cost_optimization: parseFloat(e.target.value),
                    },
                  })
                }
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Capacity Utilization"
                type="number"
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                value={parameters.objective_weights.capacity_utilization}
                onChange={(e) =>
                  setParameters({
                    ...parameters,
                    objective_weights: {
                      ...parameters.objective_weights,
                      capacity_utilization: parseFloat(e.target.value),
                    },
                  })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreate}
            variant="contained"
            disabled={isCreating}
          >
            {isCreating ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OptimizationPage;