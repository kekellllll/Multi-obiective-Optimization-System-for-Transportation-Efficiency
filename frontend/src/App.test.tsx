import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders transportation optimization app title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Multi-Objective Transportation Efficiency Optimization System/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders system status', () => {
  render(<App />);
  const statusElement = screen.getByText(/All systems operational/i);
  expect(statusElement).toBeInTheDocument();
});

test('renders metric cards', () => {
  render(<App />);
  const trainsElement = screen.getByText(/Total Trains/i);
  const routesElement = screen.getByText(/Active Routes/i);
  expect(trainsElement).toBeInTheDocument();
  expect(routesElement).toBeInTheDocument();
});
