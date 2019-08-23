#!/bin/bash

NUM_EXECUTIONS=30
NUM_THREADS=(1)

GXX=/tmp/gcc10_parallel/usr/local/bin/g++
FILE_PREFIX="$HOME/gcc_git/build_parallel/gcc/"
FILE=gimple-match.c
GXX_FLAGS="\
    -fno-pie \
    -c \
    -g \
    -O2 \
    -DIN_GCC \
    -fno-exceptions \
    -fno-rtti \
    -fasynchronous-unwind-tables \
    -W \
    -Wall \
    -Wno-narrowing \
    -Wwrite-strings \
    -Wcast-qual \
    -Wmissing-format-attribute \
    -Woverloaded-virtual \
    -pedantic \
    -Wno-long-long \
    -Wno-variadic-macros \
    -Wno-overlength-strings \
    -Wno-unused \
    -DHAVE_CONFIG_H \
    -I. \
    -I. \
    -I../../gcc/gcc \
    -I../../gcc/gcc/. \
    -I../../gcc/gcc/../include \
    -I../../gcc/gcc/../libcpp/include \
    -I../../gcc/gcc/../libdecnumber \
    -I../../gcc/gcc/../libdecnumber/bid \
    -I../libdecnumber \
    -I../../gcc/gcc/../libbacktrace \
    -o gimple-match.o \
    -MT gimple-match.o \
    -MMD \
    -MP \
    -MF \
    ./.deps/gimple-match.TPo"

TARGET_PREFIX="/tmp/data/"

do_analysis()
{
    mkdir -p $TARGET_PREFIX

    cd $FILE_PREFIX

    for thread in "${NUM_THREADS[@]}"; do
        for i in $(seq 1 $NUM_EXECUTIONS); do
            local target="${TARGET_PREFIX}time_gcc_${thread}_${i}.dat"
            local repeat=true

            while [ "$repeat" = true ]; do
                echo "In test $i with $thread threads..."

                sleep 1s
                times=$($GXX $GXX_FLAGS --param=num-threads=$thread ${FILE_PREFIX}${FILE})
                local error=$?

                if [ $error -eq 0 ]; then
                    repeat=false
                    echo "$times" > $target
                else
                    echo "Repeating test $i with $thread threads..."
                fi
            done
        done
    done
}

do_analysis
