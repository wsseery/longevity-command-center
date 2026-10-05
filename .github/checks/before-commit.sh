#!/usr/bin/env bash
# Sets BASE (in $GITHUB_ENV) to the commit the change is compared against:
#   pull_request  HEAD^1, the base branch (the checkout is GitHub's merge commit)
#   push          the previous tip of main
#   workflow_run  the commit the Weekly Longevity Update started from, so the
#                 comparison covers exactly what that run committed
# Falls back to HEAD^1 if the commit cannot be fetched.
set -u
case "$EVENT" in
  push)         want="$BEFORE" ;;
  workflow_run) want="$RUN_SHA" ;;
  *)            want="" ;;
esac
base="HEAD^1"
if [ -n "$want" ] && git fetch --no-tags --depth=1 origin "$want" 2>/dev/null; then
  base="$want"
fi
echo "BASE=$(git rev-parse "$base")" >> "$GITHUB_ENV"
echo "Comparing against $(git rev-parse --short "$base")"
