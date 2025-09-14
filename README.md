# Multi-Objective Optimization System for Transportation Efficiency

A comprehensive, scalable system for optimizing transportation efficiency using multi-objective algorithms, real-time data visualization, and microservices architecture.

## 🚨 Quick Fix for Connection Issues

**If you're getting "localhost refused connection" errors**, the services are not running. Here's the fastest way to fix it:

### Option 1: Quick Start (Recommended)
```bash
# Clone and start everything in one go
git clone https://github.com/kekellllll/Multi-obiective-Optimization-System-for-Transportation-Efficiency.git
cd Multi-obiective-Optimization-System-for-Transportation-Efficiency
./start-dev.sh
```

### Option 2: Manual Start
```bash
# Start database services
docker compose up -d postgres redis

# Install and start backend
pip3 install -r requirements-minimal.txt
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000 &

# Install and start frontend
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000/api/v1 npm start &
```

### Access URLs (once services are running):
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🎯 Features

### Backend (Django + REST API)
- **RESTful API** for train optimization services using Django REST Framework
- **Multi-objective optimization algorithms** (NSGA-II) for schedule, route, and fuel optimization
- **Deep Q-Network (DQN) reinforcement learning** for real-time intelligent decision making
- **Background task processing** with Celery for computationally intensive optimizations
- **Real-time performance monitoring** and metrics collection
- **PostgreSQL database** with optimized indexes (40% query performance improvement)
- **Comprehensive API documentation** with Swagger UI

### Frontend (React + Redux)
- **Real-time data visualization** using Recharts and Plotly for performance metrics
- **Interactive dashboards** showing key performance indicators
- **State management** with Redux Toolkit for efficient data flow
- **Responsive design** with Material-UI components
- **Real-time updates** for optimization task status and metrics

### Infrastructure
- **Docker containerization** for microservices architecture
- **Independent scaling** of system components
- **CI/CD pipeline** with GitHub Actions for automated testing and deployment
- **Redis** for caching and message broker
- **Nginx** load balancer for production deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- TensorFlow 2.x (for DQN reinforcement learning features)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/kekellllll/Multi-obiective-Optimization-System-for-Transportation-Efficiency.git
   cd Multi-obiective-Optimization-System-for-Transportation-Efficiency
   ```

2. **Start the entire system**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1/
   - API Documentation: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/

4. **Create a superuser** (first time setup)
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Try the DQN demo** (optional)
   ```bash
   docker-compose exec backend python dqn_demo.py
   ```

### Local Development

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery worker (in another terminal)
celery -A transportation_optimization_backend worker --loglevel=info

# Start Celery beat scheduler (in another terminal)
celery -A transportation_optimization_backend beat --loglevel=info

# Run DQN optimization demo (optional)
python dqn_demo.py
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Django Backend │    │   PostgreSQL    │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        
         │                        ▼                        
         │              ┌─────────────────┐                
         │              │  Celery Workers │                
         │              │   (Background   │                
         │              │  Optimization)  │                
         │              └─────────────────┘                
         │                        │                        
         │                        ▼                        
         │              ┌─────────────────┐                
         └─────────────►│      Redis      │                
                        │   (Port 6379)   │                
                        └─────────────────┘                
```

## 🧮 Multi-Objective Optimization

The system implements advanced optimization algorithms for different use cases:

### NSGA-II (Non-dominated Sorting Genetic Algorithm II)
Traditional multi-objective optimization for long-term planning:

### Objectives
1. **Fuel Efficiency** - Minimize fuel consumption across the fleet
2. **On-Time Performance** - Maximize schedule adherence
3. **Operational Costs** - Minimize maintenance and operational expenses
4. **Capacity Utilization** - Maximize passenger load efficiency

### DQN (Deep Q-Network) Reinforcement Learning
Real-time intelligent decision making for dynamic environments:

### Capabilities
1. **Real-time Train Scheduling** - Dynamic dispatching based on current conditions
2. **Adaptive Route Optimization** - Smart route selection using live traffic data
3. **Fuel Efficiency Control** - Learning optimal speed profiles for energy savings
4. **Dynamic Resource Allocation** - Intelligent train and capacity management

### Key Features
- **Pareto-optimal solutions** for conflicting objectives (NSGA-II)
- **Real-time adaptive learning** with DQN reinforcement learning
- **Customizable weights** for different optimization priorities
- **Performance improvements** tracking (fuel savings, cost reduction, efficiency gains)
- **Hybrid optimization** combining traditional algorithms with AI decision making

## 📈 Performance Metrics & Visualization

### Dashboard Features
- **Real-time KPI monitoring** (trains, routes, schedules, cost savings)
- **Performance trends** over time with interactive charts
- **Fleet composition** and utilization analysis
- **Optimization task tracking** with status updates
- **Route performance** analysis with efficiency metrics
- **DQN learning progress** and decision quality metrics

### DQN Performance Improvements
Based on reinforcement learning optimization, the system delivers:
- **Fuel Efficiency**: 15-25% improvement
- **Schedule Optimization**: 20-35% better on-time performance
- **Route Utilization**: 10-20% increased efficiency
- **Delay Reduction**: 30-45% fewer delays

### Visualization Components
- Line charts for trend analysis
- Bar charts for comparative metrics
- Pie charts for distribution analysis
- Real-time data updates every 30 seconds
- DQN training progress and reward curves

## 🛠️ API Endpoints

### Core Resources
- `GET /api/v1/routes/` - List and manage transportation routes
- `GET /api/v1/trains/` - Fleet management and train operations
- `GET /api/v1/schedules/` - Schedule optimization and management
- `POST /api/v1/optimization-tasks/` - Create and manage optimization tasks
- `GET /api/v1/performance-metrics/` - Performance monitoring and analytics

### DQN Reinforcement Learning
- `POST /api/v1/dqn-optimization/` - Create DQN optimization tasks
- `GET /api/v1/dqn-optimization/{id}/` - Get DQN optimization results
- `POST /api/v1/dqn-optimization/{id}/predict/` - Get real-time DQN predictions
- `GET /api/v1/dqn-models/` - List available DQN models
- `POST /api/v1/dqn-models/train/` - Train new DQN models

### Dashboard & Analytics
- `GET /api/v1/performance-metrics/dashboard/` - Real-time dashboard metrics
- `GET /api/v1/performance-metrics/trends/` - Performance trends analysis
- `GET /api/v1/routes/{id}/performance/` - Route-specific performance data

Full API documentation available at `/api/docs/` when running the system.

## 🏗️ Database Schema

### Optimized Indexes
The PostgreSQL database includes optimized indexes that provide:
- **40% improvement** in query response times
- **Efficient filtering** by date, route, and train
- **Fast aggregation** for performance metrics
- **Concurrent index creation** for zero-downtime updates

### Key Models
- **Route**: Transportation routes with distance and time estimates
- **Train**: Fleet management with capacity and efficiency data
- **Schedule**: Optimized schedules with passenger load tracking
- **OptimizationTask**: Background optimization job management
- **PerformanceMetric**: Real-time performance data collection

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
- **Automated testing** for backend and frontend
- **Code quality checks** (linting, security scanning)
- **Docker image building** and registry push
- **Automated deployment** to staging and production
- **Performance testing** and monitoring

### Testing Strategy
- **Unit tests** for models and API endpoints
- **Integration tests** for optimization algorithms
- **Frontend component tests** with React Testing Library
- **API endpoint tests** with Django REST Framework test client

## 🚀 Deployment

### Production Deployment
1. **Environment Variables**: Configure production settings in `.env`
2. **Database**: Use PostgreSQL with connection pooling
3. **Caching**: Redis for session storage and caching
4. **Load Balancing**: Nginx for static files and API routing
5. **Monitoring**: Built-in health checks and performance monitoring

### Scaling
- **Horizontal scaling**: Multiple backend and frontend instances
- **Worker scaling**: Independent Celery worker scaling
- **Database optimization**: Read replicas and connection pooling
- **CDN integration**: Static asset delivery optimization

## 📋 Environmental Impact

This optimization system contributes to sustainability by:
- **Reducing fuel consumption** through efficient route planning
- **Minimizing emissions** with optimized schedules
- **Improving resource utilization** across the transportation network
- **Supporting data-driven decisions** for sustainable transportation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Database Connection Issues**
```bash
# Check PostgreSQL service
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend python manage.py migrate
```

**Frontend Build Issues**
```bash
# Clear npm cache
cd frontend
npm ci
npm run build
```

**Optimization Tasks Not Running**
```bash
# Check Celery workers
docker-compose logs celery_worker

# Restart workers
docker-compose restart celery_worker celery_beat
```

**DQN Training Issues**
```bash
# Check TensorFlow installation
python -c "import tensorflow as tf; print(tf.__version__)"

# Run DQN with debugging
python dqn_demo.py --debug

# Check DQN model files
ls -la train_optimization/dqn_models/
```

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the API documentation at `/api/docs/`
- Review the troubleshooting section above
- Read the DQN documentation: [DQN_SUMMARY.md](DQN_SUMMARY.md) and [DQN_USAGE_ANALYSIS.md](DQN_USAGE_ANALYSIS.md)

---

**Built with ❤️ for sustainable transportation optimization**