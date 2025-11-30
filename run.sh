#!/bin/bash

echo "Starting FASTAPI backend..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Streamlit frontend..."
streamlit run src/frontend/app.py &
FRONTEND_PID=$!

echo "Both services started."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

echo "Press CTRL+C to stop."

wait $BACKEND_PID $FRONTEND_PID
