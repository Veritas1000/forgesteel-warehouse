#!/bin/bash -e

## Generate a version from git metadata

fallback_version='0.0.0'
project_file=$1

if [ -z "$project_file" ]
then
    project_file="pyproject.toml"
fi

## Get latest tag, trimming the 'v'
latest_tag=$(git describe --abbrev=0 --tags --match 'v*.*.*' 2>/dev/null | sed 's/^v//')

if [ -z "$latest_tag" ]
then
    latest_tag="$fallback_version"
fi

## see if current commit is tagged
this_commit_tag=$(git tag -l 'v*.*.*' --points-at HEAD | sed 's/^v//')

if [ "$this_commit_tag" = "$latest_tag" ]
then
    version="$latest_tag"
else
    ## append date and commit hash
    timestamp=$(date '+%Y%m%d%H%M%S')
    hash=$(git rev-parse --short HEAD)
    version="${latest_tag}+d${timestamp}-g${hash}"
fi

## write to pyproject.toml
sed -i "s/^version =.*$/version = \"${version}\"/" "$project_file"
# echo "__version__ = \"${version}\"" > $project_file

echo $version
