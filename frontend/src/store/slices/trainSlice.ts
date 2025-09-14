import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Train, LoadingState } from '../../types';
import { trainApi } from '../../services/api';

interface TrainState extends LoadingState {
  trains: Train[];
  currentTrain: Train | null;
  operationalTrains: Train[];
}

const initialState: TrainState = {
  trains: [],
  currentTrain: null,
  operationalTrains: [],
  loading: false,
  error: null,
};

export const fetchTrains = createAsyncThunk(
  'trains/fetchTrains',
  async (params?: Record<string, any>) => {
    const response = await trainApi.getAll(params);
    return response.data;
  }
);

export const fetchTrain = createAsyncThunk(
  'trains/fetchTrain',
  async (id: number) => {
    const response = await trainApi.get(id);
    return response.data;
  }
);

export const createTrain = createAsyncThunk(
  'trains/createTrain',
  async (data: Partial<Train>) => {
    const response = await trainApi.create(data);
    return response.data;
  }
);

export const updateTrain = createAsyncThunk(
  'trains/updateTrain',
  async ({ id, data }: { id: number; data: Partial<Train> }) => {
    const response = await trainApi.update(id, data);
    return response.data;
  }
);

export const deleteTrain = createAsyncThunk(
  'trains/deleteTrain',
  async (id: number) => {
    await trainApi.delete(id);
    return id;
  }
);

export const fetchOperationalTrains = createAsyncThunk(
  'trains/fetchOperationalTrains',
  async () => {
    const response = await trainApi.getOperational();
    return response.data;
  }
);

const trainSlice = createSlice({
  name: 'trains',
  initialState,
  reducers: {
    clearCurrentTrain: (state) => {
      state.currentTrain = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch trains
      .addCase(fetchTrains.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTrains.fulfilled, (state, action) => {
        state.loading = false;
        state.trains = action.payload.results;
      })
      .addCase(fetchTrains.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch trains';
      })
      // Fetch single train
      .addCase(fetchTrain.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTrain.fulfilled, (state, action) => {
        state.loading = false;
        state.currentTrain = action.payload;
      })
      .addCase(fetchTrain.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch train';
      })
      // Create train
      .addCase(createTrain.fulfilled, (state, action) => {
        state.trains.push(action.payload);
      })
      // Update train
      .addCase(updateTrain.fulfilled, (state, action) => {
        const index = state.trains.findIndex(train => train.id === action.payload.id);
        if (index !== -1) {
          state.trains[index] = action.payload;
        }
        if (state.currentTrain?.id === action.payload.id) {
          state.currentTrain = action.payload;
        }
      })
      // Delete train
      .addCase(deleteTrain.fulfilled, (state, action) => {
        state.trains = state.trains.filter(train => train.id !== action.payload);
        if (state.currentTrain?.id === action.payload) {
          state.currentTrain = null;
        }
      })
      // Fetch operational trains
      .addCase(fetchOperationalTrains.fulfilled, (state, action) => {
        state.operationalTrains = action.payload;
      });
  },
});

export const { clearCurrentTrain, clearError } = trainSlice.actions;
export default trainSlice.reducer;