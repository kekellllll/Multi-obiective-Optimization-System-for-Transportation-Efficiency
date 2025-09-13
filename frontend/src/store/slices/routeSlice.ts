import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Route, LoadingState } from '../../types';
import { routeApi } from '../../services/api';

interface RouteState extends LoadingState {
  routes: Route[];
  currentRoute: Route | null;
  activeRoutes: Route[];
}

const initialState: RouteState = {
  routes: [],
  currentRoute: null,
  activeRoutes: [],
  loading: false,
  error: null,
};

export const fetchRoutes = createAsyncThunk(
  'routes/fetchRoutes',
  async (params?: Record<string, any>) => {
    const response = await routeApi.getAll(params);
    return response.data;
  }
);

export const fetchRoute = createAsyncThunk(
  'routes/fetchRoute',
  async (id: number) => {
    const response = await routeApi.get(id);
    return response.data;
  }
);

export const createRoute = createAsyncThunk(
  'routes/createRoute',
  async (data: Partial<Route>) => {
    const response = await routeApi.create(data);
    return response.data;
  }
);

export const updateRoute = createAsyncThunk(
  'routes/updateRoute',
  async ({ id, data }: { id: number; data: Partial<Route> }) => {
    const response = await routeApi.update(id, data);
    return response.data;
  }
);

export const deleteRoute = createAsyncThunk(
  'routes/deleteRoute',
  async (id: number) => {
    await routeApi.delete(id);
    return id;
  }
);

export const fetchActiveRoutes = createAsyncThunk(
  'routes/fetchActiveRoutes',
  async () => {
    const response = await routeApi.getActive();
    return response.data;
  }
);

const routeSlice = createSlice({
  name: 'routes',
  initialState,
  reducers: {
    clearCurrentRoute: (state) => {
      state.currentRoute = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch routes
      .addCase(fetchRoutes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoutes.fulfilled, (state, action) => {
        state.loading = false;
        state.routes = action.payload.results;
      })
      .addCase(fetchRoutes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch routes';
      })
      // Fetch single route
      .addCase(fetchRoute.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoute.fulfilled, (state, action) => {
        state.loading = false;
        state.currentRoute = action.payload;
      })
      .addCase(fetchRoute.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch route';
      })
      // Create route
      .addCase(createRoute.fulfilled, (state, action) => {
        state.routes.push(action.payload);
      })
      // Update route
      .addCase(updateRoute.fulfilled, (state, action) => {
        const index = state.routes.findIndex(route => route.id === action.payload.id);
        if (index !== -1) {
          state.routes[index] = action.payload;
        }
        if (state.currentRoute?.id === action.payload.id) {
          state.currentRoute = action.payload;
        }
      })
      // Delete route
      .addCase(deleteRoute.fulfilled, (state, action) => {
        state.routes = state.routes.filter(route => route.id !== action.payload);
        if (state.currentRoute?.id === action.payload) {
          state.currentRoute = null;
        }
      })
      // Fetch active routes
      .addCase(fetchActiveRoutes.fulfilled, (state, action) => {
        state.activeRoutes = action.payload;
      });
  },
});

export const { clearCurrentRoute, clearError } = routeSlice.actions;
export default routeSlice.reducer;