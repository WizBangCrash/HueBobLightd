#!/bin/sh
# Synology DSM bootup script
# Save to /usr/local/etc/rc.d and make sure its chmod 755
# Configured Variables:
PYTHON_EXEC="/volume1/@appstore/py3k/usr/local/bin/python3"
EXEC="/volume1/@appstore/py3k/usr/local/bin/hueboblightd"
CONFIG="/var/services/homes/david/HueBobLightd/hueboblightd.conf"
LOG_DIR="/var/services/homes/david/HueBobLightd/logs"

# Begin script
case "$1" in
start)
  printf "%-30s" "Starting hueboblightd"
  ${EXEC} --config ${CONFIG} --logdir ${LOG_DIR} >&/dev/null &
  printf "[%4s]\n" "done"
  ;;
stop)
  printf "%-30s" "Stopping hueboblightd"
  printf "[%4s]\n" "done"
  ;;
*)
  echo "Usage: $0 {start|stop}"
  exit 1
esac

exit 0