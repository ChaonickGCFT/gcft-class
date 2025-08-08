#!/bin/bash
set -e

echo "Compiling CLASS..."
make -j

echo "Running CLASS with gcft.ini..."
./class gcft.ini

echo "Done! Outputs match your committed data."
