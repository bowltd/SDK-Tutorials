#!/bin/bash

wget https://github.com/opencv/opencv/archive/refs/tags/4.5.1.zip
unzip 4.5.1.zip
rm 4.5.1.zip
mv opencv-* opencv
cd opencv
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=$(pwd)/../../../../install ..
make -j4 install