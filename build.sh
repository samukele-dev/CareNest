#!/bin/bash
# build.sh

echo "🚀 Building CareNest..."

# Backend
echo "🐍 Setting up Django..."
pip install -r backend/requirements.txt

# Frontend
echo "⚛️ Building React frontend..."
cd frontend
npm install
npm run build
cd babckend

# Django setup
echo "📦 Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "🗄️ Running migrations..."
python backend/manage.py migrate

echo "✅ Build complete!"