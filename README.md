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

## ⚙️ Getting Started & Installation

### Prerequisites
- Docker
- Docker Compose

### 1. Environment Setup

**For Development:**
Create a `.env.local` file in the root directory. Development uses the local Docker `db` service.
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://ecommerce_user:yourpassword@db:5432/ecommerce_db

# Docker database variables
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432

# Other integrations (Cloudinary, Payments, etc.)
```

**For Production:**
Create a `.env` file in the root directory. Production requires an external database (e.g. Supabase, AWS RDS).
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-external-database-url
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1

# Other integrations (Cloudinary, Payments, etc.)
```

### 2. Build the Docker Image
First, build the Docker image used by the web and celery services:
```sh
docker build -t sellaris:latest -f Dockerfile .
```

### 3. Run the Project

**Development Environment:**
```sh
# Start the containers in the background
docker compose --env-file .env.local -f docker-compose.yml up -d

# Run database migrations
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py migrate

# Create an admin user (optional)
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py createsuperuser
```
The API will be available at `http://localhost:8000/`.

**Production Environment:**
```sh
# Recommended for Redis performance in production
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf

# Start the containers in the background
docker compose --env-file .env -f docker-compose.prod.yml up -d

# Run database migrations
docker compose --env-file .env -f docker-compose.prod.yml exec web python3 manage.py migrate

# Collect static files
docker compose --env-file .env -f docker-compose.prod.yml exec web python3 manage.py collectstatic --no-input
```
The API will be served via Nginx at `http://localhost/` (or your configured domain).

## 🔒 Enabling HTTPS

This project uses dynamic Nginx configuration. You **do not** need to manually edit Nginx config files!

### 1. Update your `.env` file
Add your domain details to your production `.env` file:
```env
DOMAIN_NAME=yourdomain.com
INCLUDE_WWW=true  # Optional: Set to true if you want to also support www.yourdomain.com
```

### 2. Get your SSL Certificate
Before running this, make sure:
- Your domain points to your server's IP address.
- Ports `80` and `443` are open on your server firewall.

Run Certbot to fetch the certificate:
```sh
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```
*(Make sure to replace `yourdomain.com` and `your@email.com` in the command above with your actual details).*

Once the certificate is generated, restart the stack so Nginx can pick it up:
```sh
docker compose -f docker-compose.prod.yml down
docker compose --env-file .env -f docker-compose.prod.yml up -d
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
