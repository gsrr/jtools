#!/bin/bash

echo 1 > /sys/block/sdb/device/timeout
echo 1000 > /sys/block/sdb/device/qnap_param_latency