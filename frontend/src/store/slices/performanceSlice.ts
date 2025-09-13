import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { PerformanceMetric, DashboardMetrics, LoadingState } from '../../types';
import { performanceApi } from '../../services/api';

interface PerformanceState extends LoadingState {
  metrics: PerformanceMetric[];
  currentMetric: PerformanceMetric | null;
  dashboardMetrics: DashboardMetrics | null;
  trends: any;
  summary: any;
}

const initialState: PerformanceState = {
  metrics: [],
  currentMetric: null,
  dashboardMetrics: null,
  trends: null,
  summary: null,
  loading: false,
  error: null,
};

export const fetchPerformanceMetrics = createAsyncThunk(
  'performance/fetchMetrics',
  async (params?: Record<string, any>) => {
    const response = await performanceApi.getAll(params);
    return response.data;
  }
);

export const fetchPerformanceMetric = createAsyncThunk(
  'performance/fetchMetric',
  async (id: number) => {
    const response = await performanceApi.get(id);
    return response.data;
  }
);

export const createPerformanceMetric = createAsyncThunk(
  'performance/createMetric',
  async (data: Partial<PerformanceMetric>) => {
    const response = await performanceApi.create(data);
    return response.data;
  }
);

export const fetchDashboardMetrics = createAsyncThunk(
  'performance/fetchDashboard',
  async () => {
    const response = await performanceApi.getDashboard();
    return response.data;
  }
);

export const fetchPerformanceTrends = createAsyncThunk(
  'performance/fetchTrends',
  async ({ type, days }: { type: string; days?: number }) => {
    const response = await performanceApi.getTrends(type, days);
    return response.data;
  }
);

export const fetchPerformanceSummary = createAsyncThunk(
  'performance/fetchSummary',
  async () => {
    const response = await performanceApi.getSummary();
    return response.data;
  }
);

const performanceSlice = createSlice({
  name: 'performance',
  initialState,
  reducers: {
    clearCurrentMetric: (state) => {
      state.currentMetric = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    addRealTimeMetric: (state, action) => {
      state.metrics.unshift(action.payload);
      // Keep only the latest 100 metrics in memory
      if (state.metrics.length > 100) {
        state.metrics = state.metrics.slice(0, 100);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch metrics
      .addCase(fetchPerformanceMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPerformanceMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload.results;
      })
      .addCase(fetchPerformanceMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch performance metrics';
      })
      // Fetch single metric
      .addCase(fetchPerformanceMetric.fulfilled, (state, action) => {
        state.currentMetric = action.payload;
      })
      // Create metric
      .addCase(createPerformanceMetric.fulfilled, (state, action) => {
        state.metrics.unshift(action.payload);
      })
      // Fetch dashboard metrics
      .addCase(fetchDashboardMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.dashboardMetrics = action.payload;
      })
      .addCase(fetchDashboardMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch dashboard metrics';
      })
      // Fetch trends
      .addCase(fetchPerformanceTrends.fulfilled, (state, action) => {
        state.trends = action.payload;
      })
      // Fetch summary
      .addCase(fetchPerformanceSummary.fulfilled, (state, action) => {
        state.summary = action.payload;
      });
  },
});

export const { clearCurrentMetric, clearError, addRealTimeMetric } = performanceSlice.actions;
export default performanceSlice.reducer;