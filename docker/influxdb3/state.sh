# Sourced by init.sh with STATE_DIR (and RUN_USER for state_exec) set; requires the /app/state volume.
if [ ! -d /app/state ]; then
  echo "state: /app/state is not mounted - enable State on this deployment" >&2
  exit 1
fi
mkdir -p "$STATE_DIR"

state_exec() {
  run_group=$(id -g "$RUN_USER")
  if chown "$RUN_USER:$run_group" "$STATE_DIR"; then
    find "$STATE_DIR" ! -user "$RUN_USER" -exec chown "$RUN_USER:$run_group" {} +
    run_as=$RUN_USER
  else
    run_as=$(stat -c %u:%g "$STATE_DIR")
  fi
  echo "state: $STATE_DIR owned by $(stat -c %u:%g "$STATE_DIR"), starting as $run_as"
  exec gosu "$run_as" "$@"
}
