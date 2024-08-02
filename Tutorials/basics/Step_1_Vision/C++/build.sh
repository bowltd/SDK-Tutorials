#!/bin/bash

set -e

rm -rf build
mkdir build
cd build
cmake ..
make -j4
chmod +x bow_tutorial_1
cp bow_tutorial_1 ..