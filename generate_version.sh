#!/bin/bash -e

## Generate a version from git metadata

fallback_version='0.0.0'
version_file=$1

if [[ -z "$version_file" ]]
then
    version_file="forgesteel_warehouse/__version__.py"
fi

## Get latest tag, trimming the 'v'
latest_tag=$(git describe --abbrev=0 --tags --match 'v*.*.*' 2>/dev/null | sed 's/^v//')

if [[ -z "$latest_tag" ]]
then
    latest_tag="$fallback_version"
fi

## see if current commit is tagged
this_commit_tag=$(git tag -l 'v*.*.*' --points-at HEAD | sed 's/^v//')

if [ "$this_commit_tag" == "$latest_tag" ]
then
    version="$latest_tag"
else
    ## append date and commit hash
    timestamp=$(date '+%Y%m%d%H%M%S')
    hash=$(git rev-parse --short HEAD)
    version="${latest_tag}-${timestamp}-${hash}"
fi

## write to __version__.py
echo "__version__ = \"${version}\"" > $version_file

echo $version