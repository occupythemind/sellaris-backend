# 🛒 Sellaris — Django E-Commerce Engine

A scalable and secure e-commerce backend API built with Django and Django REST Framework.
This project provides core commerce functionality including product management, cart handling, orders, and more — designed with production-level architecture in mind.

## 🚀 Features
- Product catalog management
- Shopping cart system
- Wishlist functionality
- Order processing workflow
- RESTful API design
- Dockerized development environment
- Modular and scalable architecture (domain-based apps)

## 📡 Available API Endpoints
```
/api/v1/products/
/api/v1/carts/
/api/v1/wishlists/
/api/v1/orders/
/api/v1/payments/
/api/v1/users/
```
⚠️ Note: This project is actively in development. More endpoints and features will be added.

## 🧱 Tech Stack
Backend: Django, Django REST Framework
Database: PostgreSQL
Containerization: Docker
Async (planned): Celery + Redis

## ⚙️ Getting Started
Prerequisites
- Docker
- Docker Compose

## 🔧 Run the Project
```
docker compose --env-file .env -f docker/docker-compose.yml up --build
```

## 🛠️ Environment Variables

Create a .env file in the root directory and configure:
```
DEBUG=True
SECRET_KEY=your-secret-key

# For docker
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432

# For Django
DATABASE_URL=postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
```

## 📂 Project Structure
```
apps/
├── users/
├── products/
├── cart/
├── orders/
├── payments/
└── notifications/

core/
services/
tasks/
config/
apps/ → Domain-based modules
core/ → Shared utilities and configurations
services/ → Business logic layer
tasks/ → Background jobs (Celery-ready)
```

## 🧠 Architecture Highlights
- Decoupled backend (API-first design)
- Service-layer architecture for business logic
- Modular app structure for scalability
- Designed for future microservices transition

## 🔐 Security Considerations (In Progress)
- Secure payment verification
- Input validation and data integrity checks
- Rate limiting (planned)

## 🛠️ Roadmap
- Payment integration (Flutterwave / Paystack)
- Authentication & authorization (Guest user also supported)
- Product variants & inventory system
- Order tracking & status updates
- Email notifications via Celery (planned)
- API rate limiting
- Admin dashboard enhancements (planned)

## 📌 Status

`🚧 Work in Progress — actively being developed and improved.`

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome.
Feel free to fork the project or open an issue.

## 📄 License

This project is open-source and available under the MIT License.
