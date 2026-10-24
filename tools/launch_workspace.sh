#!/usr/bin/env bash
# Opens the AI GroupChat workspace for MMM-ML:
#   1. starts the room server (:8765) and Model Studio (:8766) if they are not already running,
#   2. opens the room in the default browser,
#   3. opens three Ghostty windows in the project folder running Claude Code, Codex and
#      Antigravity (agy). Each runs inside an interactive bash so ~/.bashrc (nvm, PATH) loads,
#      and the window stays open with a shell if the agent exits.
# Usage: launch_workspace.sh [--dry-run]     (--dry-run prints what it would do)
set -u

PROJECT="/home/sarvn/Documents/MMM-ML"
ROOM_PORT=8765
STUDIO_PORT=8766
LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/ai-groupchat"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

run() { if [ $DRY -eq 1 ]; then printf 'would run:'; printf ' %q' "$@"; echo; else "$@"; fi; }
port_up() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }
say() { echo "$*"; [ $DRY -eq 0 ] && command -v notify-send >/dev/null && notify-send -a "AI GroupChat" "AI GroupChat" "$*"; }

cd "$PROJECT" || { say "Project folder not found: $PROJECT"; exit 1; }
mkdir -p "$LOG_DIR"

# 1. servers (left running in the background; logs in ~/.cache/ai-groupchat/)
if port_up "$ROOM_PORT"; then echo "room already running on :$ROOM_PORT"
else
  if [ $DRY -eq 1 ]; then run python3 collaboration/group_chat.py serve
  else nohup python3 collaboration/group_chat.py serve >"$LOG_DIR/room.log" 2>&1 & fi
fi
if port_up "$STUDIO_PORT"; then echo "Model Studio already running on :$STUDIO_PORT"
elif [ -x .venv/bin/python ]; then
  if [ $DRY -eq 1 ]; then run .venv/bin/python -W ignore app/server.py
  else nohup .venv/bin/python -W ignore app/server.py >"$LOG_DIR/studio.log" 2>&1 & fi
fi
if [ $DRY -eq 0 ]; then
  for _ in $(seq 1 40); do port_up "$ROOM_PORT" && break; sleep 0.25; done
  port_up "$ROOM_PORT" || say "The room did not start; see $LOG_DIR/room.log"
fi

# 2. the room in the browser
if [ $DRY -eq 1 ]; then run xdg-open "http://127.0.0.1:$ROOM_PORT"
else xdg-open "http://127.0.0.1:$ROOM_PORT" >/dev/null 2>&1 & fi

# 3. one Ghostty window per agent
open_agent() {  # $1 window title, $2 agent command
  local title="$1" cmd="$2"
  if ! bash -ic "command -v ${cmd%% *}" >/dev/null 2>&1; then say "$cmd is not installed; skipped its terminal"; return; fi
  local inner="$cmd; echo; echo '[$title exited. This shell stays open.]'; exec bash"
  if [ $DRY -eq 1 ]; then run ghostty --gtk-single-instance=false --title="$title" --working-directory="$PROJECT" -e bash -ic "$inner"
  else nohup ghostty --gtk-single-instance=false --title="$title" --working-directory="$PROJECT" -e bash -ic "$inner" >/dev/null 2>&1 &
  fi
}
command -v ghostty >/dev/null || { say "Ghostty is not installed"; exit 1; }
open_agent "Claude · MMM-ML" "claude"
open_agent "Codex · MMM-ML" "codex"
open_agent "Gemini (Antigravity) · MMM-ML" "agy"

[ $DRY -eq 0 ] && say "Room, Claude, Codex and Gemini are opening."
exit 0
