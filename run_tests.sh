#!/bin/sh

SERVER="server-mc57874.py"  # Filename of server
TEST_DIR="tests"

PORT_BASE=$(( ($RANDOM % 5100)+1200 ))
for i in {1..6}; do
    # spawn server
    python3 $SERVER "$PORT_BASE$i" &> /dev/null &
    # wait for server to start
    sleep 0.1
    # run test script
    python3 "$TEST_DIR/Test$i.py" "127.0.0.1" "$PORT_BASE$i" | grep 'SUMMARY'

    # kill server
    kill $!
    wait $! 2> /dev/null
done
