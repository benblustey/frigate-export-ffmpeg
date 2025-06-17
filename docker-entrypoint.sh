#!/bin/bash

# Start cron in the background
service cron start

# Keep the container running
tail -f /var/log/cron.log 