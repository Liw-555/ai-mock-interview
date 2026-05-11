#!/bin/bash
# Stop Interview Agent services

echo "Stopping Interview Agent services..."

# Kill Python backend (uvicorn)
pkill -f "uvicorn main:app" 2>/dev/null && echo "Backend stopped" || echo "Backend not running"

# Kill Node frontend (vite)
pkill -f "vite" 2>/dev/null && echo "Frontend stopped" || echo "Frontend not running"

echo "Done."
