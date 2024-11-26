#!/bin/bash

set -e

rm -rf build
mkdir build
cd build
cmake ..
make -j4
chmod +x bow_ext_sonar
cp bow_ext_sonar ..