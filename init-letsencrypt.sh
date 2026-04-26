#!/bin/bash

# Initialize Let's Encrypt certificates for the Nginx container
# This script creates dummy certificates to allow Nginx to start,
# then uses Certbot to replace them with real certificates.

COMPOSE_FILE="docker-compose.prod.yml"

if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: docker is not installed.' >&2
  exit 1
fi

if [ ! -f .env ]; then
  echo 'Error: .env file not found. Please create it and define DOMAIN_NAME and DOMAIN_MAIL.'
  exit 1
fi

# Extract variables from .env
DOMAIN_NAME=$(grep -E "^DOMAIN_NAME=" .env | cut -d '=' -f 2 | tr -d '"'\'' ')
DOMAIN_MAIL=$(grep -E "^DOMAIN_MAIL=" .env | cut -d '=' -f 2 | tr -d '"'\'' ')

if [ -z "$DOMAIN_NAME" ] || [ -z "$DOMAIN_MAIL" ]; then
  echo "Error: DOMAIN_NAME or DOMAIN_MAIL is not set in .env."
  exit 1
fi

INCLUDE_WWW=$(grep -E "^INCLUDE_WWW=" .env | cut -d '=' -f 2 | tr -d '"'\'' ' | tr '[:upper:]' '[:lower:]')

DOMAIN=$DOMAIN_NAME
EMAIL=$DOMAIN_MAIL

DOMAIN_ARGS="-d $DOMAIN"
if [ "$INCLUDE_WWW" = "true" ] || [ "$INCLUDE_WWW" = "1" ] || [ "$INCLUDE_WWW" = "yes" ]; then
  DOMAIN_ARGS="-d $DOMAIN -d www.$DOMAIN"
  echo "ℹ️ Including www.$DOMAIN in the certificate request."
else
  echo "ℹ️ Requesting certificate for $DOMAIN only (set INCLUDE_WWW=true in .env to include www)."
fi

echo "### Creating dummy certificate for $DOMAIN ..."
# Run a temporary certbot container to generate a dummy certificate
docker compose -f $COMPOSE_FILE run --rm --entrypoint sh certbot -c "\
  mkdir -p /etc/letsencrypt/live/$DOMAIN && \
  openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj \"/CN=localhost\""

echo "### Starting nginx ..."
docker compose -f $COMPOSE_FILE up --force-recreate -d nginx

echo "### Waiting for Nginx to start..."
sleep 5

echo "### Deleting dummy certificate for $DOMAIN ..."
docker compose -f $COMPOSE_FILE run --rm --entrypoint sh certbot -c "\
  rm -Rf /etc/letsencrypt/live/$DOMAIN && \
  rm -Rf /etc/letsencrypt/archive/$DOMAIN && \
  rm -Rf /etc/letsencrypt/renewal/$DOMAIN.conf"

echo "### Requesting Let's Encrypt certificate for $DOMAIN ..."
if ! docker compose -f $COMPOSE_FILE run --rm --entrypoint sh certbot -c "\
  certbot certonly --webroot -w /var/www/certbot \
    $DOMAIN_ARGS \
    --email $EMAIL \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal \
    --no-eff-email"; then
  echo "❌ ERROR: Certbot failed to obtain the certificate."
  echo "Please check the Certbot output above to see why it failed."
  exit 1
fi

echo "### Starting all services and reloading nginx ..."
docker compose -f $COMPOSE_FILE up -d
docker compose -f $COMPOSE_FILE exec nginx nginx -s reload

echo "### Done! Let's Encrypt certificates have been successfully provisioned."
