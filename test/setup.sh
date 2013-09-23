d="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd $d > /dev/null 2>&1
export MACHINEFEATURES=`pwd`/m
export JOBFEATURES=`pwd`/j
popd > /dev/null 2>&1
