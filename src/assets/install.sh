#!/bin/bash

# Installation script for Linux systems

if ! id "tmsauser" &>/dev/null; then
    sudo useradd -r -s /bin/false tmsauser
fi

sudo mkdir -p /var/lib/tmsa
sudo mkdir -p /var/log/tmsa

sudo chown tmsauser:tmsauser /var/lib/tmsa
sudo chown tmsauser:tmsauser /var/log/tmsa

sudo chmod -R 755 /var/lib/tmsa
sudo chmod -R 755 /var/log/tmsa

echo "Time Matters setup completed."
