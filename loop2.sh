#! /bin/bash
fileName="readme.txt"
directoryName="workshop"
listName="list.txt"
mkdir $diretoryName
cd $diretoryName
touch $fileName
for i in {1..5}; do
echo "$i" >> $fileName
done
echo "Content of the $fileName:"
cat $fileName
ls > $listName
echo "Content of the $listName:"
cat $listName
