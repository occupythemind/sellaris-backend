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
```sh
docker build -t sellaris:latest -f Dockerfile .

# On Development
docker compose --env-file .env.local -f docker-compose.yml up
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py migrate

# On Production 
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
docker compose --env-file .env -f docker-compose.prod.yml up
docker compose --env-file .env -f docker-compose.prod.yml exec web python3 manage.py migrate
```

## 🛠️ Environment Variables

### On Development
Create a .env.local file in the root directory and configure:
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

### On Production
Create a .env file in the root directory and configure:

## For HTTPS

### Update Nginx:
In the `nginx/nginx.conf`, replace `api-sellaris.gleeze.com ` with your domain name (eg. example.com).
```conf
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://web:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Get your Certificate:
Before this, make sure:
- Your domain points to your server IP
- Ports 80 and 443 are open

```
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
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
