#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <image-tag>"
  exit 1
fi

IMAGE_TAG="$1"
DEPLOY_DIR="${DEPLOY_DIR:-$HOME/f1bot-backend}"
TMP_IMAGE="/tmp/f1bot-backend-image.tar.gz"
TMP_COMPOSE="/tmp/docker-compose.prod.yml"
TMP_ENV="/tmp/f1bot-backend.env"

mkdir -p "$DEPLOY_DIR"

if [[ -f "$TMP_COMPOSE" ]]; then
  mv "$TMP_COMPOSE" "$DEPLOY_DIR/docker-compose.yml"
else
  echo "Missing $TMP_COMPOSE"
  exit 1
fi

if [[ -f "$TMP_ENV" ]]; then
  mv "$TMP_ENV" "$DEPLOY_DIR/.env"
else
  echo "Missing $TMP_ENV"
  exit 1
fi

if [[ -f "$TMP_IMAGE" ]]; then
  gunzip -c "$TMP_IMAGE" | docker load
  rm -f "$TMP_IMAGE"
else
  echo "Missing $TMP_IMAGE"
  exit 1
fi

cd "$DEPLOY_DIR"

# Persist the image tag so manual compose restarts do not try to pull defaults.
if grep -q '^BACKEND_IMAGE=' .env; then
  sed -i "s|^BACKEND_IMAGE=.*|BACKEND_IMAGE=${IMAGE_TAG}|" .env
else
  printf "\nBACKEND_IMAGE=%s\n" "$IMAGE_TAG" >> .env
fi

BACKEND_IMAGE="$IMAGE_TAG" docker compose up -d --remove-orphans

# Keep host disk usage bounded.
docker image prune -f >/dev/null 2>&1 || true

echo "Deployment complete with image: $IMAGE_TAG"
