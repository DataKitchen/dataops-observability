#!/usr/bin/env sh
set -e

# This script merges the current commit into the given target branch. The
# source branch is only given as a parameter to include in the commit message.

exit_with_status() {
  exit_code=$1
  shift
  for a in "$@"
  do
    echo "$a"
  done
  exit "$exit_code"
}

if [ "$#" -ne 2 ]
then
  exit_with_status 1 "Usage: $(basename "$0") <source branch> <target branch>" \
    "N.B: <source branch> is only used for the commit message"
fi

SOURCE_COMMIT=$(git rev-parse HEAD)
SOURCE_BRANCH=$1
TARGET_BRANCH=$2

if [ "$(git rev-parse --is-shallow-repository)" = "true" ]
then
  # Need unshallow for `git cherry` to work
  git fetch --unshallow origin HEAD "$TARGET_BRANCH"
else
  git fetch origin HEAD "$TARGET_BRANCH"
fi
git -c advice.detachedHead=false checkout "origin/$TARGET_BRANCH"

UNMERGED_COMMITS=$(git cherry "$SOURCE_COMMIT" HEAD)
if [ "$(echo "$UNMERGED_COMMITS" | grep -cE '^\+')" -gt 0 ]
then
  exit_with_status 1 "error: branch '$TARGET_BRANCH' has unmerged commits:"\
    "$UNMERGED_COMMITS"
fi

git merge --no-ff "$SOURCE_COMMIT" \
  -m "Promote branch '$SOURCE_BRANCH' into $TARGET_BRANCH"

if [ "$(git rev-parse "origin/$TARGET_BRANCH")" = "$(git rev-parse HEAD)" ]
then
  exit_with_status 0 "No merge required, exiting"
fi

git push origin "HEAD:$TARGET_BRANCH"
