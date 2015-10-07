#!/bin/bash
MOOSEPATH=`pwd`
echo "+ I am in $MOOSEPATH"
( 
    cd $MOOSEPATH && mkdir -p _build && cd _build && cmake $CMAKE_FLAGS ..
    make -j8
    ctest --output-on-failure
)
