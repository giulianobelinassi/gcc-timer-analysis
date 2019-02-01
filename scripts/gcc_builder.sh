#!/bin/bash

PATH_TO_SOURCE=$1
PATH_TO_BUILD=$2
PATH_TO_OUTDATA=$3
NUM_JOBS=$4

LAUNCHED_PATH=$PWD
PATH_TO_ME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

print_usage_message()
{
    echo "Time analyzer for the GCC project."
    echo "Usage: <PATH_TO_SOURCE> <PATH_TO_BUILD> <NUM_JOBS>"
    echo "where:"
    echo "  <PATH_TO_SOURCE>        Path to gcc source code"
    echo "  <PATH_TO_BUILD>         Path to where gcc will be built"
    echo "  <PATH_TO_OUTFILE>       Path to where the timing data will be written"
    echo "  <NUM_JOBS>              Number of Makefile jobs"
    echo "  Any other parameter will be passed to gcc configure"
    echo ""
    echo "This program is Free Software and is distributed under the GNU Public License"
    echo "version 2. There is no warranty; not even from MERCHANTABILITY or FITNESS FOR"
    echo "A PARTICULAR PURPOSE."
}

create_wrapper()
{
    cd $PATH_TO_ME/cc_wrapper

    make OUTPUT_FILE=$PATH_TO_OUTDATA TARGET_CC_PATH=$1 TARGET_CC_NAME=$2 \
        TARGET_CXX_PATH=$3 TARGET_CXX_NAME=$4

}

prepare_gcc()
{
    local whereis_gcc=$(whereis gcc | awk '{print $2}')
    local whereis_gxx=$(whereis g++ | awk '{print $2}')

    create_wrapper "$whereis_gcc" "gcc" "$whereis_gxx" "g++"

    cd $PATH_TO_BUILD
    CC=$PATH_TO_ME/cc_wrapper/gcc CXX=$PATH_TO_ME/cc_wrapper/g++ \
        $PATH_TO_SOURCE/configure "$@"

    cd $LAUNCHED_PATH
}


create_xgcc()
{
    cd $PATH_TO_BUILD

    make -j$NUM_JOBS all-gcc

    cd $LAUNCHED_PATH
}

wrap_xgcc()
{
    cd $PATH_TO_BUILD/gcc

    local whereis_gcc="$PATH_TO_BUILD/gcc/_xgcc"
    local whereis_gxx="$PATH_TO_BUILD/gcc/_xg++"

    mv xgcc _xgcc
    mv xg++ _xg++

    create_wrapper "$whereis_gcc" "$whereis_gcc" "$whereis_gxx" "$whereis_gxx"

    mv $PATH_TO_ME/cc_wrapper/xgcc $PATH_TO_BUILD/gcc/xgcc
    mv $PATH_TO_ME/cc_wrapper/xg++ $PATH_TO_BUILD/gcc/xg++

    cd $LAUNCHED_PATH
}

continue_stage1()
{
    cd $PATH_TO_BUILD

    make -j$NUM_JOBS stage1-bubble

    cd $LAUNCHED_PATH
}

create_directories()
{
    mkdir -p $PATH_TO_BUILD
}

if [ $# -lt 4 ]; then
    print_usage_message
    exit
fi

shift 4

create_directories
prepare_gcc
create_xgcc
wrap_xgcc
continue_stage1
