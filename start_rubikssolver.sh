#!/bin/bash
# Start/stop a local web server for the Rubik's Solver
# Usage: ./start_rubikssolver.sh [--stop] [--restart]

PORT=8080
PIDFILE="/tmp/rubikssolver.pid"

stop_server() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID"
      echo "Stopped server (PID $PID)"
    fi
    rm -f "$PIDFILE"
  else
    echo "No server running."
  fi
}

start_server() {
  # Kill any existing server on this port
  lsof -ti:$PORT | xargs kill 2>/dev/null

  cd "$(dirname "$0")"
  echo "Starting Rubik's Solver on http://localhost:$PORT"
  echo "Open that URL in your browser. Press Ctrl+C to stop."
  python3 -m http.server $PORT &
  echo $! > "$PIDFILE"
  echo "Server PID: $(cat $PIDFILE)"
  echo ""
  echo "Or just open index.html directly in your browser — no server needed!"
}

case "$1" in
  --stop)
    stop_server
    ;;
  --restart)
    stop_server
    start_server
    ;;
  *)
    start_server
    ;;
esac
