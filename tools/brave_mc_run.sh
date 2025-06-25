#!/bin/sh
# File: brave_mcp_run.sh
# Usage: ./brave_mcp_run.sh python my_dspy_script.py "your query here"

set -eu  # abort on error or undefined var

### ── CONFIG ───────────────────────────────
BRAVE_API_KEY="${BRAVE_API_KEY:-XXXXX}"   # export in your shell or hard-code
MCP_CMD="brave-search-mcp serve --stdio"  # same as before
PID_FILE="/tmp/brave_mcp.pid"             # any writable location

### ── START MCP IN BACKGROUND ─────────────
echo "▶ Starting Brave MCP …"
env BRAVE_API_KEY="$BRAVE_API_KEY" $MCP_CMD >/tmp/brave_mcp.log 2>&1 &
echo $! > "$PID_FILE"                     # save PID
sleep 1                                   # give it a moment to bind stdio

### ── CLEAN-UP FUNCTION ───────────────────
cleanup() {
  if [ -f "$PID_FILE" ]; then
    MCP_PID=$(cat "$PID_FILE")
    echo "▶ Stopping Brave MCP (PID $MCP_PID)…"
    kill "$MCP_PID" 2>/dev/null || true
    rm -f "$PID_FILE"
  fi
}
trap cleanup INT TERM EXIT                # run on script exit or Ctrl-C

### ── RUN YOUR DSPy PIPELINE ─────────────
"$@"