#!/bin/bash

# Basic while loop
# This loop counts integers less than 3
counter=0
while [ counter -lt 3 ]; # We can increase the integers in the loop by modifying the figure in the counter
do
echo $counter
    ((counter++)) # increases the variable counter by 1
done


# + is addtion
# - is subtraction
# \* is multiplication
# / division
# var++ increases variable var by 1
# var-- decreases the variable var by 1
# % mudulus (remainder after division)

# CONTROL OPERATORS
# ; normal separator between commands
# && execute next command if the first command succeeds
# || execure next command only if the second command fails

