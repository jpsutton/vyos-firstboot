#!/bin/vbash

RUN_FLAG="/config/.firstboot-done"
FIRST_BOOT_FILE="/tmp/vyos-firstboot.cfg"

# Exit immediately if we've already run once
if [ -f "$RUN_FLAG" ]; then
  echo "INFO: First boot config has been applied already; exiting." >&2
  exit 0
fi

# Template for vyos scripts
source /opt/vyatta/etc/functions/script-template

function find_iso9660_dev {
  for blkdev in $(ls /dev/block); do
    blkid "/dev/block/${blkdev}" | grep 'TYPE="iso9660"' > /dev/null

    if [ $? -eq 0 ]; then
      echo "/dev/block/${blkdev}"
      return
    fi
  done
}

# Attempt to extract vyosinit.cfg from the first detected CD/DVD device
python3 /usr/bin/vyos-firstboot.py $(find_iso9660_dev)

# If anything was found, it will be dropped in /tmp/vyos-firstboot.cfg
if [ -f "$FIRST_BOOT_FILE" ]; then
  # Enter configuration mode
  configure

  # Load the configuration file
  load "$FIRST_BOOT_FILE"

  # Commit and save the configuration
  commit
  save
fi

touch "$RUN_FLAG"
