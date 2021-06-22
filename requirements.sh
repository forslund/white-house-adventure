ROOT=`pwd`
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}

#build frotz
git submodule update --init frotz
cd frotz
make dumb
cd ..
