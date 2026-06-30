num=6
if [ $num -gt 5 ] && [ $num -le 7 ] # if the number is greater than 5 and less than 7; then do something
then # the do something is printing "number is 6 or 7"
    echo "$num is 6 or 7"
elif [ $num -lt 0 ] || [ $num -eq 0 ]; # do something, if the number is not greater than 5 and less than 7
then # if the number is less than zero or equal to zero, then do something else "print the number is negative or zero"
    echo "$num is negative or zero"
else # if the number is none of the above conditional statements, then do something totally different; that is, print "num is negative (but not 6, 7 or zero)"
    echo "$num is negative (but not 6, 7 or zero)
fi

num=6
if (( $num % 2 == 0)) # This number is equal to then num; this means that multiplying 6 by 2 is equals to zero;
    then # This statement is actually true
    echo "This number is an even number !"
fi