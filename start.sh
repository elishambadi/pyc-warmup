#!/bin/bash

echo "🔄 Pulling latest changes from git..."
git pull

echo "🛑 Stopping Docker containers..."
docker compose down

echo "🚀 Starting Docker containers..."
docker compose up -d

echo "✅ Done! Containers are running."
