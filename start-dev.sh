#!/bin/bash

# Multi-Objective Optimization System Startup Script
# This script starts the application services in development mode

echo "🚀 Starting Multi-Objective Optimization System for Transportation Efficiency"
echo "=================================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ $service_name is ready!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}✗ $service_name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Step 1: Start database services with Docker Compose
echo -e "\n${BLUE}1. Starting database services (PostgreSQL & Redis)...${NC}"
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not installed or not available${NC}"
    exit 1
fi

docker compose up -d postgres redis
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start database services${NC}"
    exit 1
fi

# Wait for databases to be ready
echo -e "${YELLOW}Waiting for databases to be ready...${NC}"
sleep 10

# Step 2: Check if Python dependencies are installed
echo -e "\n${BLUE}2. Checking Python dependencies...${NC}"
if [ ! -d "$HOME/.local/lib/python3.12/site-packages/django" ] && [ ! -d "/usr/local/lib/python3.12/site-packages/django" ]; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -r requirements-minimal.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Python dependencies${NC}"
        exit 1
    fi
fi

# Step 3: Setup Django (migrations, static files)
echo -e "\n${BLUE}3. Setting up Django...${NC}"
mkdir -p static
python3 manage.py migrate
python3 manage.py collectstatic --noinput --clear >/dev/null 2>&1

# Step 4: Start Django backend
echo -e "\n${BLUE}4. Starting Django backend...${NC}"
if check_port 8000; then
    echo -e "${YELLOW}Port 8000 is already in use. Checking if it's our Django server...${NC}"
    if curl -s http://localhost:8000/admin/ | grep -q "Django"; then
        echo -e "${GREEN}✓ Django backend is already running${NC}"
    else
        echo -e "${RED}Port 8000 is occupied by another service${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Starting Django development server...${NC}"
    nohup python3 manage.py runserver 0.0.0.0:8000 >/dev/null 2>&1 &
    DJANGO_PID=$!
    
    # Wait for Django to be ready
    if ! wait_for_service "http://localhost:8000/admin/" "Django backend"; then
        kill $DJANGO_PID 2>/dev/null
        exit 1
    fi
fi

# Step 5: Setup and start React frontend
echo -e "\n${BLUE}5. Setting up React frontend...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Node.js dependencies${NC}"
        exit 1
    fi
fi

# Start React development server
echo -e "\n${BLUE}6. Starting React frontend...${NC}"
if check_port 3000; then
    echo -e "${YELLOW}Port 3000 is already in use. Checking if it's our React server...${NC}"
    if curl -s http://localhost:3000/ | grep -q "react"; then
        echo -e "${GREEN}✓ React frontend is already running${NC}"
    else
        echo -e "${RED}Port 3000 is occupied by another service${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Starting React development server...${NC}"
    REACT_APP_API_URL=http://localhost:8000/api/v1 nohup npm start >/dev/null 2>&1 &
    REACT_PID=$!
    
    # Wait for React to be ready
    if ! wait_for_service "http://localhost:3000/" "React frontend"; then
        kill $REACT_PID 2>/dev/null
        exit 1
    fi
fi

cd ..

# Step 7: Final verification
echo -e "\n${BLUE}7. Final verification...${NC}"
echo -e "${YELLOW}Testing all endpoints...${NC}"

endpoints=(
    "http://localhost:3000/ Frontend"
    "http://localhost:8000/api/v1/ Backend_API"
    "http://localhost:8000/api/docs/ API_Documentation"
    "http://localhost:8000/admin/ Admin_Panel"
)

all_working=true
for endpoint in "${endpoints[@]}"; do
    url=$(echo "$endpoint" | cut -d' ' -f1)
    name=$(echo "$endpoint" | cut -d' ' -f2)
    
    if curl -s -f -I "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $name: $url${NC}"
    elif curl -s -I "$url" | grep -q "403\|302"; then
        # 403 (API requires auth) and 302 (admin redirect) are expected
        echo -e "${GREEN}✓ $name: $url${NC}"
    else
        echo -e "${RED}✗ $name: $url${NC}"
        all_working=false
    fi
done

echo -e "\n=================================================================="
if [ "$all_working" = true ]; then
    echo -e "${GREEN}🎉 All services are running successfully!${NC}"
    echo ""
    echo -e "${BLUE}Access the application:${NC}"
    echo -e "  • Frontend: ${GREEN}http://localhost:3000${NC}"
    echo -e "  • Backend API: ${GREEN}http://localhost:8000/api/v1/${NC}"
    echo -e "  • API Documentation: ${GREEN}http://localhost:8000/api/docs/${NC}"
    echo -e "  • Admin Panel: ${GREEN}http://localhost:8000/admin/${NC}"
    echo ""
    echo -e "${YELLOW}Note: The API requires authentication. Use the admin panel to create users.${NC}"
    echo -e "${YELLOW}To stop services, use 'docker compose down' and terminate the Python/Node processes.${NC}"
else
    echo -e "${RED}❌ Some services failed to start. Check the logs above.${NC}"
    exit 1
fi