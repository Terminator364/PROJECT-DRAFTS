#!/usr/bin/env bash
set -euo pipefail
echo "REPOSITORY_RECIPE_MISSING:chatgpt-pc.sh" >&2
echo "This BuildHub version requires the production branch to provide .matrix-build/build.sh." >&2
echo "Refusing to execute a stale central build recipe." >&2
exit 74
