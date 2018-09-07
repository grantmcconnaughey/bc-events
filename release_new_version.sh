#!/bin/sh

for dist_file_path in dist/*; do
    dist_file=${dist_file_path##*/}
    exists=$(aws s3 ls s3://$PIP_BUCKET/$dist_file)
    if [ -z "$exists" ]; then
        aws s3 cp "dist/$dist_file" "s3://$PIP_BUCKET/$dist_file"
    else
        echo "$dist_file already exists, skipping upload."
    fi
done
