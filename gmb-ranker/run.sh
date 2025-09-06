#!/bin/bash

# Ensure the script is run from its own directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run install.bat or install.sh first."
    exit 1
fi

# Start Flask application in the background and log stdout/stderr
echo "Starting Flask application in the background..."
python3 app.py > flask_server.log 2> flask_server.err &
FLASK_PID=$!
sleep 5 # Give the server a moment to start

# Trigger the simulation
echo "Triggering simulation for business: 'Eiffel Tower'..."
curl -X POST http://127.0.0.1:5001/run-simulation \
    -H "Content-Type: application/json" \
    -d '{
        "search_term": "Eiffel Tower",
        "business_name": "Eiffel Tower",
        "latitude": 48.8584,
        "longitude": 2.2945,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }'
SIMULATION_RESPONSE=$?

if [ $SIMULATION_RESPONSE -eq 0 ]; then
    echo "Simulation started successfully!"
else
    echo "Failed to trigger simulation. See curl error above."
    kill $FLASK_PID
    exit 1
fi

# Wait for a fixed time for the simulation to complete.
# This is a simple approach; a more robust solution might involve polling a status endpoint.
echo "Waiting for simulation to complete (fixed 120 second wait)..."
sleep 120

# Shutdown the Flask server
echo "Shutting down Flask server..."
kill $FLASK_PID
wait $FLASK_PID 2>/dev/null

# --- Verification ---
echo "--- Flask Server Log ---"
cat flask_server.log

echo "--- Flask Server Errors ---"
cat flask_server.err

# Check if the final "Simulation finished" message is in the log
if grep -q "Simulation finished." flask_server.log; then
    echo "------------------------"
    echo "SUCCESS: 'Simulation finished.' message found in log."
    echo "------------------------"
    # Optional: Clean up log file
    # rm flask_server.log
else
    echo "------------------------"
    echo "FAILURE: 'Simulation finished.' message NOT found in log."
    echo "------------------------"
    # Optional: Keep log for debugging
fi

# Deactivate virtual environment
deactivate
