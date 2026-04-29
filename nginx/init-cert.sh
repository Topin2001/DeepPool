#!/bin/bash
# Lancer UNE SEULE FOIS avant de démarrer la stack complète.
# Usage : bash nginx/init-cert.sh votre-domaine@email.com mondomaine.duckdns.org

set -e

EMAIL=$1
DOMAIN=$2

if [[ -z "$EMAIL" || -z "$DOMAIN" ]]; then
  echo "Usage : $0 <email> <domaine>"
  exit 1
fi

# Remplace YOUR_DOMAIN dans la config nginx
sed -i "s/YOUR_DOMAIN/$DOMAIN/g" nginx/nginx.conf

echo "→ Démarrage nginx seul (HTTP uniquement pour le challenge ACME)..."
docker compose up -d nginx

echo "→ Demande du certificat Let's Encrypt..."
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN"

echo "→ Redémarrage de la stack complète..."
docker compose up -d

echo "✓ Certificat obtenu. Renouvellement automatique actif."