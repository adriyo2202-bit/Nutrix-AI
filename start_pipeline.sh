#!/bin/bash
`    echo "Ollama is expected to be running locally on port 11434"

    echo "Starting FastAPI Backend..."
    nohup python3 "Scource code/nutrix_ai/api.py" > backend.log 2>&1 &

    echo "Starting Web Frontend..."
    cd frontend && nohup python3 server_no_cache.py > frontend.log 2>&1 &

    echo "Pipeline started successfully!"
    echo "AI Server:   Ollama on port 11434"
    echo "Backend API: http://localhost:8000"
    echo "Frontend:    http://localhost:3000"
`
