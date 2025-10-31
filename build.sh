#!/bin/bash
set -e

echo "Installing Node.js dependencies..."
cd frontend
npm ci
echo "Building frontend..."
npm run build
cd ..

echo "Copying frontend build to backend static folder..."
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

echo "Build completed successfully!"

