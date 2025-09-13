import { configureStore } from '@reduxjs/toolkit';
import trainReducer from './slices/trainSlice';
import routeReducer from './slices/routeSlice';
import scheduleReducer from './slices/scheduleSlice';
import optimizationReducer from './slices/optimizationSlice';
import performanceReducer from './slices/performanceSlice';

export const store = configureStore({
  reducer: {
    trains: trainReducer,
    routes: routeReducer,
    schedules: scheduleReducer,
    optimization: optimizationReducer,
    performance: performanceReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;