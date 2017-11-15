#!/bin/bash
cat output.txt |
while IFS= read -r line || [[ -n "$line" ]]; do
    echo "Text read from file: $line"
    echo <(`casperjs post.js --inline $line >> posts.txt`)
    echo "waiting"
done
