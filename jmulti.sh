#!/bin/bash

multipath -F
systemctl restart multipathd
multipath -ll
