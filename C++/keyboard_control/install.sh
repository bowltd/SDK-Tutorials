#!/bin/bash

set -e

rm -rf build
mkdir build
cd build
cmake ..
make -j4
cp bow_keyboard_control ..