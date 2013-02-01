#!/bin/bash
{ sleep 0.5; echo "duck: $1"; } | telnet localhost 47974
