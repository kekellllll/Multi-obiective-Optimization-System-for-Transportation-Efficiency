import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { OptimizationTask, LoadingState } from '../../types';
import { optimizationApi } from '../../services/api';

interface OptimizationState extends LoadingState {
  tasks: OptimizationTask[];
  currentTask: OptimizationTask | null;
  myTasks: OptimizationTask[];
  isCreating: boolean;
}

const initialState: OptimizationState = {
  tasks: [],
  currentTask: null,
  myTasks: [],
  loading: false,
  isCreating: false,
  error: null,
};

export const fetchOptimizationTasks = createAsyncThunk(
  'optimization/fetchTasks',
  async (params?: Record<string, any>) => {
    const response = await optimizationApi.getAll(params);
    return response.data;
  }
);

export const fetchOptimizationTask = createAsyncThunk(
  'optimization/fetchTask',
  async (id: number) => {
    const response = await optimizationApi.get(id);
    return response.data;
  }
);

export const createOptimizationTask = createAsyncThunk(
  'optimization/createTask',
  async (data: { optimization_type: string; parameters: Record<string, any> }) => {
    const response = await optimizationApi.create(data);
    return response.data;
  }
);

export const restartOptimizationTask = createAsyncThunk(
  'optimization/restartTask',
  async (id: number) => {
    await optimizationApi.restart(id);
    return id;
  }
);

export const fetchMyTasks = createAsyncThunk(
  'optimization/fetchMyTasks',
  async () => {
    const response = await optimizationApi.getMyTasks();
    return response.data;
  }
);

const optimizationSlice = createSlice({
  name: 'optimization',
  initialState,
  reducers: {
    clearCurrentTask: (state) => {
      state.currentTask = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateTaskStatus: (state, action) => {
      const { taskId, status, results } = action.payload;
      const task = state.tasks.find(t => t.task_id === taskId);
      if (task) {
        task.status = status;
        if (results) {
          task.results = results;
        }
      }
      const myTask = state.myTasks.find(t => t.task_id === taskId);
      if (myTask) {
        myTask.status = status;
        if (results) {
          myTask.results = results;
        }
      }
      if (state.currentTask?.task_id === taskId) {
        state.currentTask.status = status;
        if (results) {
          state.currentTask.results = results;
        }
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch tasks
      .addCase(fetchOptimizationTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOptimizationTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload.results;
      })
      .addCase(fetchOptimizationTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch optimization tasks';
      })
      // Fetch single task
      .addCase(fetchOptimizationTask.fulfilled, (state, action) => {
        state.currentTask = action.payload;
      })
      // Create task
      .addCase(createOptimizationTask.pending, (state) => {
        state.isCreating = true;
        state.error = null;
      })
      .addCase(createOptimizationTask.fulfilled, (state, action) => {
        state.isCreating = false;
        state.tasks.unshift(action.payload);
        state.myTasks.unshift(action.payload);
      })
      .addCase(createOptimizationTask.rejected, (state, action) => {
        state.isCreating = false;
        state.error = action.error.message || 'Failed to create optimization task';
      })
      // Restart task
      .addCase(restartOptimizationTask.fulfilled, (state, action) => {
        const taskId = action.payload;
        const updateTaskStatus = (task: OptimizationTask) => {
          if (task.id === taskId) {
            task.status = 'pending';
            task.error_message = '';
            task.start_time = undefined;
            task.end_time = undefined;
          }
        };
        state.tasks.forEach(updateTaskStatus);
        state.myTasks.forEach(updateTaskStatus);
        if (state.currentTask?.id === taskId) {
          updateTaskStatus(state.currentTask);
        }
      })
      // Fetch my tasks
      .addCase(fetchMyTasks.fulfilled, (state, action) => {
        state.myTasks = action.payload;
      });
  },
});

export const { clearCurrentTask, clearError, updateTaskStatus } = optimizationSlice.actions;
export default optimizationSlice.reducer;