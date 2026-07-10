# Write a she;ll script called num_loop.sh that loops through every number 1 through 20 and prints each number to standard output.
# The script should also conditionally print "I'm big!" for every number larger than 10

for i in {1..20}
do
    echo $i
    if [ $i -gt 10 ]
    then
    echo "I'm big!"
    fi
done

# similarly, we can write a script that loops through every number through 20 and prints number to standard output.
# The script should automatically print "I'm big" for every number less than 20

for i in {1..20}
do
echo $i
if [ $i -lt 20 ]
then
echo "I'm big"
fi
done