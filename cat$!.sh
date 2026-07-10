cat $1 &> /dev/null
if [ $? -eq 0 ]; then
    echo "This file exists"
else
    echo "This file does not exist"
fi