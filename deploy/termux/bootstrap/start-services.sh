#!/data/data/com.termux/files/usr/bin/sh
exec 2>&1

# AIOS-node Termux cold-boot service bootstrap (N4 / NODE-003B)
# Establishes deterministic environment, writes host-local boot marker,
# and starts the termux-services service-daemon supervisor exactly once.
# Does not own AIOS execution, Executors, Git, network, verification, retry,
# wake locks, or publication.

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
HOME="${HOME:-/data/data/com.termux/files/home}"
SVDIR="${SVDIR:-$PREFIX/var/service}"
LOGDIR="${LOGDIR:-$HOME/.aios-node/logs}"
MARKER_DIR="${MARKER_DIR:-$HOME/.aios-node/bootstrap/markers}"

export PREFIX HOME SVDIR LOGDIR

mkdir -p "$LOGDIR" "$MARKER_DIR"

BOOT_ID=""
if [ -r /proc/sys/kernel/random/boot_id ]; then
    read -r BOOT_ID < /proc/sys/kernel/random/boot_id
fi

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date 2>/dev/null || echo "unknown")"

# Write bounded host-local boot marker for physical cold-boot qualification
printf '{"timestamp":"%s","boot_id":"%s","event":"BOOTSTRAP_DISPATCH"}\n' "$TIMESTAMP" "$BOOT_ID" > "$MARKER_DIR/last_boot.marker"

# Invoke service supervisor daemon exactly once
exec "$PREFIX/bin/service-daemon" start
