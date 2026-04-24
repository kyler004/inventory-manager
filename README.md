# Inventory Manager

A comprehensive inventory management system built with Django REST Framework backend and React TypeScript frontend.

## Overview

This project implements a full-featured inventory management system designed for businesses to track products, stock levels, suppliers, purchase orders, and more. The system provides real-time stock monitoring, automated alerts, reporting capabilities, and a modern web interface.

## Architecture

### Backend (Django)

- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT tokens with refresh/blacklist support
- **Real-time**: Django Channels for WebSocket connections
- **Task Queue**: Celery with Redis for background tasks
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)
- **Additional Features**:
  - Audit logging for all changes
  - Import/Export functionality
  - CORS support for frontend integration
  - Custom user model with role-based permissions

### Frontend (React)

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form with Zod validation
- **Routing**: React Router v7
- **Charts**: Recharts for data visualization
- **UI Components**: Custom components with class-variance-authority

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Web Server**: Nginx (production)
- **Reverse Proxy**: Nginx for API and static files

## Features

### Core Modules

1. **Authentication & Users**
   - JWT-based authentication
   - Role-based permissions (Admin, Manager, Staff)
   - User management

2. **Products**
   - Product catalog with categories (hierarchical)
   - Product variants (size, color, etc.)
   - SKU and barcode support
   - Unit of measure management
   - Cost and retail pricing
   - Tax rates

3. **Locations & Stock**
   - Multi-location support (warehouses, stores)
   - Zone-based organization within locations
   - Real-time stock level tracking
   - Reorder point management
   - Reserved quantity tracking

4. **Suppliers & Purchase Orders**
   - Supplier management
   - Purchase order creation and tracking
   - Batch tracking for received goods

5. **Stock Transfers**
   - Internal stock transfers between locations
   - Transfer approval workflow

6. **Alerts & Notifications**
   - Low stock alerts
   - Expiry date warnings
   - Custom alert rules
   - Real-time notifications via WebSockets

7. **Reports**
   - Inventory reports
   - Sales reports
   - Stock movement reports
   - Profit margin analysis

### API Features

- RESTful API design
- OpenAPI/Swagger documentation
- Filtering, searching, and pagination
- Bulk operations support
- Audit trail for all changes

## Current Implementation Status

### Completed ✅

- **Models**:
  - User authentication and roles
  - Product catalog with categories and variants
  - Location and zone management
  - Supplier management
- **API Endpoints**:
  - Authentication (login/logout)
  - Basic CRUD for products, locations, suppliers
- **Frontend**:
  - Project setup with React/TypeScript/Vite
  - Basic routing and layout
  - Authentication forms
- **Infrastructure**:
  - Docker Compose setup for development
  - PostgreSQL and Redis services
  - Basic Django project structure

### In Progress 🚧

- **Stock Management Models**: Core stock level tracking
- **Purchase Orders**: Full implementation
- **Batch Tracking**: For inventory batches
- **Alerts System**: Notification framework
- **Reports Module**: Report generation
- **Frontend Pages**: Dashboard, product management, etc.

### Planned 📋

- **Stock Transfers**: Between locations
- **Real-time Dashboard**: Live stock monitoring
- **Mobile App**: React Native companion
- **Advanced Reporting**: Charts and analytics
- **Integration APIs**: Third-party service connections
- **Production Deployment**: Complete Docker setup

## Project Structure

```
inventory-manager/
├── backend/                    # Django backend
│   ├── apps/                   # Django apps
│   │   ├── authentication/     # Auth endpoints
│   │   ├── products/          # Product management
│   │   ├── locations/         # Location/zone management
│   │   ├── stock/             # Stock level tracking
│   │   ├── suppliers/         # Supplier management
│   │   ├── purchase_orders/   # PO system
│   │   ├── batches/           # Batch tracking
│   │   ├── transfers/         # Stock transfers
│   │   ├── alerts/            # Notification system
│   │   ├── reports/           # Reporting module
│   │   ├── users/             # User management
│   │   └── tests/             # Test utilities
│   ├── config/                # Django settings
│   ├── core/                  # Shared utilities
│   └── requirements/          # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── store/             # Zustand stores
│   │   ├── types/             # TypeScript types
│   │   └── lib/               # Utilities
│   └── public/                # Static assets
├── docker/                    # Docker files
├── docker-compose.yml         # Development setup
├── docker-compose.prod.yml    # Production setup
└── .env.example              # Environment variables template
```

## Setup & Development

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Quick Start

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd inventory-manager
   ```

2. **Environment Setup**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start Development Environment**

   ```bash
   docker-compose up -d
   ```

4. **Backend Setup**

   ```bash
   cd backend
   pip install -r requirements/development.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

5. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Running Tests

```bash
cd backend
pytest
```

### API Documentation

When running, visit `http://localhost:8000/api/docs/` for Swagger UI.

## Development Guidelines

### Backend

- Follow Django REST Framework best practices
- Use serializers for all API responses
- Implement proper permission classes
- Write comprehensive tests for all features
- Use migrations for database changes

### Frontend

- Use TypeScript for all components
- Follow React hooks patterns
- Implement proper error handling
- Use TanStack Query for server state
- Maintain consistent styling with Tailwind

### Code Quality

- Run linters: `npm run lint` (frontend), `black` (backend)
- Write tests for new features
- Follow conventional commit messages
- Use pre-commit hooks for quality checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.
