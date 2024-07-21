#!/bin/bash



# Check if the text file is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <text file>"
    exit 1
fi

# Read the text file line by line
while IFS=' ' read -r filename cid; do
    # Check if both filename and cid are present
    if [ -n "$filename" ] && [ -n "$cid" ]; then
        # Execute the ipfs get command
        ipfs get --progress=true "$cid" -o "$filename"
    else
        echo "Invalid line: $filename $cid"
    fi
done < "$1"
