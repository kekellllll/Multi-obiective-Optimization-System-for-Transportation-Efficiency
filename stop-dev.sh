#!/bin/bash

# Multi-Objective Optimization System Shutdown Script
# This script stops all application services

echo "🛑 Stopping Multi-Objective Optimization System for Transportation Efficiency"
echo "=================================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Stop Docker services
echo -e "\n${BLUE}1. Stopping Docker services...${NC}"
docker compose down
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker services stopped${NC}"
else
    echo -e "${YELLOW}⚠ Failed to stop Docker services (they might not be running)${NC}"
fi

# Stop Django backend
echo -e "\n${BLUE}2. Stopping Django backend...${NC}"
DJANGO_PIDS=$(ps aux | grep "[p]ython3 manage.py runserver" | awk '{print $2}')
if [ -n "$DJANGO_PIDS" ]; then
    echo "$DJANGO_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✓ Django backend stopped${NC}"
else
    echo -e "${YELLOW}⚠ No Django backend processes found${NC}"
fi

# Stop React frontend
echo -e "\n${BLUE}3. Stopping React frontend...${NC}"
REACT_PIDS=$(ps aux | grep "[n]pm start" | awk '{print $2}')
NODE_PIDS=$(ps aux | grep "[n]ode.*react-scripts" | awk '{print $2}')

if [ -n "$REACT_PIDS" ]; then
    echo "$REACT_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✓ React frontend (npm) stopped${NC}"
fi

if [ -n "$NODE_PIDS" ]; then
    echo "$NODE_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✓ React frontend (node) stopped${NC}"
fi

if [ -z "$REACT_PIDS" ] && [ -z "$NODE_PIDS" ]; then
    echo -e "${YELLOW}⚠ No React frontend processes found${NC}"
fi

# Stop Celery workers if any
echo -e "\n${BLUE}4. Stopping Celery workers...${NC}"
CELERY_PIDS=$(ps aux | grep "[c]elery.*worker" | awk '{print $2}')
if [ -n "$CELERY_PIDS" ]; then
    echo "$CELERY_PIDS" | xargs kill 2>/dev/null
    echo -e "${GREEN}✓ Celery workers stopped${NC}"
else
    echo -e "${YELLOW}⚠ No Celery worker processes found${NC}"
fi

# Clean up any remaining processes
echo -e "\n${BLUE}5. Cleaning up...${NC}"
sleep 2

# Check if ports are still occupied
PORT_3000=$(lsof -ti :3000)
PORT_8000=$(lsof -ti :8000)

if [ -n "$PORT_3000" ]; then
    echo -e "${YELLOW}Force killing processes on port 3000...${NC}"
    kill -9 $PORT_3000 2>/dev/null
fi

if [ -n "$PORT_8000" ]; then
    echo -e "${YELLOW}Force killing processes on port 8000...${NC}"
    kill -9 $PORT_8000 2>/dev/null
fi

echo -e "\n=================================================================="
echo -e "${GREEN}🛑 All services have been stopped!${NC}"
echo -e "${BLUE}To restart the application, run: ./start-dev.sh${NC}"