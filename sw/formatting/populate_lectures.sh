#!/bin/sh
#
# populate_lectures.sh
# Copies the lecture template into each empty class subdirectory under lectures/,
# renaming it to Lecture<CC>_week<WW>.md based on the parent directory names.
#
# Usage: ./populate_lectures.sh

set -e

TEMPLATE="./template Lecture_week_.md"

if [ ! -f "$TEMPLATE" ]; then
    echo "ERROR: Template file not found at '$TEMPLATE'" >&2
    exit 1
fi

# Iterate over week directories
for week_dir in ./week_*/; do
    # Extract the week number from 'week_WW/'
    # e.g. 'lectures/week_01/' -> '01'
    week_base="${week_dir#./week_}"
    week_num="${week_base%/}"

    for class_dir in "${week_dir}class_01/" "${week_dir}class_02/"; do
        # Extract the class number from 'class_CC/'
        # e.g. 'class_01/' -> '01'
        class_base="${class_dir##*/class_}"
        class_num="${class_base%/}"

        # Check if the directory contains any non-hidden files
        # Use /bin/ls -A to list all files except . and ..
        # If the output is empty (or only .DS_Store), the dir is empty
        listing=$(/bin/ls -A "$class_dir" 2>/dev/null | grep -v '^\.DS_Store$' || true)

        if [ -z "$listing" ]; then
            dest_name="lecture${class_num}_week${week_num}.md"
            echo "Populating: ${class_dir}${dest_name}"
            /bin/cp "$TEMPLATE" "${class_dir}${dest_name}"
        else
            echo "Skipping (not empty): ${class_dir}"
        fi
    done
done

echo ""
echo "Done."