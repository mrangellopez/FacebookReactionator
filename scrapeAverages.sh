#!/bin/bash
cat names_ids.txt |
while IFS= read -r line || [[ -n "$line" ]]; do
    echo "Text read from file: $line"
    echo <(`casperjs average.js --inline $line >> posts.txt`)
    echo "waiting"
done
