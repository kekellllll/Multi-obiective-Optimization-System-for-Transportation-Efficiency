import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Schedule, LoadingState } from '../../types';
import { scheduleApi } from '../../services/api';

interface ScheduleState extends LoadingState {
  schedules: Schedule[];
  currentSchedule: Schedule | null;
  todaySchedules: Schedule[];
  upcomingSchedules: Schedule[];
}

const initialState: ScheduleState = {
  schedules: [],
  currentSchedule: null,
  todaySchedules: [],
  upcomingSchedules: [],
  loading: false,
  error: null,
};

export const fetchSchedules = createAsyncThunk(
  'schedules/fetchSchedules',
  async (params?: Record<string, any>) => {
    const response = await scheduleApi.getAll(params);
    return response.data;
  }
);

export const fetchSchedule = createAsyncThunk(
  'schedules/fetchSchedule',
  async (id: number) => {
    const response = await scheduleApi.get(id);
    return response.data;
  }
);

export const createSchedule = createAsyncThunk(
  'schedules/createSchedule',
  async (data: Partial<Schedule>) => {
    const response = await scheduleApi.create(data);
    return response.data;
  }
);

export const updateSchedule = createAsyncThunk(
  'schedules/updateSchedule',
  async ({ id, data }: { id: number; data: Partial<Schedule> }) => {
    const response = await scheduleApi.update(id, data);
    return response.data;
  }
);

export const deleteSchedule = createAsyncThunk(
  'schedules/deleteSchedule',
  async (id: number) => {
    await scheduleApi.delete(id);
    return id;
  }
);

export const fetchTodaySchedules = createAsyncThunk(
  'schedules/fetchTodaySchedules',
  async () => {
    const response = await scheduleApi.getToday();
    return response.data;
  }
);

export const fetchUpcomingSchedules = createAsyncThunk(
  'schedules/fetchUpcomingSchedules',
  async () => {
    const response = await scheduleApi.getUpcoming();
    return response.data;
  }
);

const scheduleSlice = createSlice({
  name: 'schedules',
  initialState,
  reducers: {
    clearCurrentSchedule: (state) => {
      state.currentSchedule = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch schedules
      .addCase(fetchSchedules.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSchedules.fulfilled, (state, action) => {
        state.loading = false;
        state.schedules = action.payload.results;
      })
      .addCase(fetchSchedules.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch schedules';
      })
      // Fetch single schedule
      .addCase(fetchSchedule.fulfilled, (state, action) => {
        state.currentSchedule = action.payload;
      })
      // Create schedule
      .addCase(createSchedule.fulfilled, (state, action) => {
        state.schedules.push(action.payload);
      })
      // Update schedule
      .addCase(updateSchedule.fulfilled, (state, action) => {
        const index = state.schedules.findIndex(schedule => schedule.id === action.payload.id);
        if (index !== -1) {
          state.schedules[index] = action.payload;
        }
        if (state.currentSchedule?.id === action.payload.id) {
          state.currentSchedule = action.payload;
        }
      })
      // Delete schedule
      .addCase(deleteSchedule.fulfilled, (state, action) => {
        state.schedules = state.schedules.filter(schedule => schedule.id !== action.payload);
        if (state.currentSchedule?.id === action.payload) {
          state.currentSchedule = null;
        }
      })
      // Fetch today's schedules
      .addCase(fetchTodaySchedules.fulfilled, (state, action) => {
        state.todaySchedules = action.payload;
      })
      // Fetch upcoming schedules
      .addCase(fetchUpcomingSchedules.fulfilled, (state, action) => {
        state.upcomingSchedules = action.payload;
      });
  },
});

export const { clearCurrentSchedule, clearError } = scheduleSlice.actions;
export default scheduleSlice.reducer;