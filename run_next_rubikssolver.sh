#!/bin/bash
# One-time tasks for Rubik's Solver project
# Usage: ./run_next_rubikssolver.sh <command>

case "$1" in
  "")
    echo "Available commands:"
    echo "  open     - Open index.html in your default browser"
    echo "  size     - Show file sizes"
    echo "  validate - Check HTML validity"
    echo ""
    ;;
  open)
    open "$(dirname "$0")/index.html"
    echo "Opened index.html in browser"
    ;;
  size)
    echo "File sizes:"
    ls -lh "$(dirname "$0")/index.html"
    wc -l "$(dirname "$0")/index.html"
    ;;
  validate)
    echo "Checking for syntax issues..."
    # Basic check: ensure script tags are balanced
    OPEN=$(grep -c '<script' "$(dirname "$0")/index.html")
    CLOSE=$(grep -c '</script>' "$(dirname "$0")/index.html")
    if [ "$OPEN" -eq "$CLOSE" ]; then
      echo "Script tags balanced: $OPEN open, $CLOSE close"
    else
      echo "WARNING: Script tag mismatch! $OPEN open, $CLOSE close"
    fi
    echo "File looks OK (open in browser to fully test)"
    ;;
  *)
    echo "Unknown command: $1"
    echo "Run without arguments to see available commands."
    ;;
esac
