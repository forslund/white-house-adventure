ROOT=`pwd`

#build frotz
git submodule update --init frotz
cd frotz
make dumb
cd ..

#download zork
mkdir zork
cd zork
wget --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" http://www.infocom-if.org/downloads/zork1.zip
unzip zork1.zip

cd ${ROOT}
