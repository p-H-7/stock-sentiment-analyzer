#!/bin/bash

echo "Setting up Stock Sentiment Analyzer..."

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
echo "Setting up frontend..."
cd ../frontend
npm install

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Start backend: cd backend && uvicorn app.main:app --reload"
echo "2. Start frontend: cd frontend && npm start"
echo "3. Start database: docker compose -f docker-compose.dev.yml up -d"
