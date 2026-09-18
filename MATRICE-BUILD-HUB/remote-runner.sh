#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:?repo name}"
BRANCH="${2:?branch}"
SOURCE_SHA="${3:?sha}"
RECIPE_PATH="${4:?recipe}"
TIMEOUT_MINUTES="${5:?timeout}"
MATRIX_REPO="${6:?repo}"
BUILD_ID="${7:?build id}"
MODE="${8:-Build}"

case "$BRANCH" in
  *[!A-Za-z0-9._/-]*|*..*|*//*)
    echo "INVALID_BRANCH"
    exit 64
    ;;
esac

cd "/workspaces/$REPO_NAME"
git fetch origin "$BRANCH"
git checkout --detach "$SOURCE_SHA"
test "$(git rev-parse HEAD)" = "$SOURCE_SHA"

mkdir -p .matrix-build-output

if [ "$MODE" = "Smoke" ]; then
  test "${CODESPACES:-}" = "true"
  test "${GITHUB_REPOSITORY:-}" = "$MATRIX_REPO"
  test -f "$RECIPE_PATH"
  bash -n "$RECIPE_PATH"
  bash -n /tmp/matrix-build-fallback.sh
  free -h
  df -h /workspaces
  curl --retry 2 --retry-all-errors -fsSIL --max-time 20 https://github.com >/dev/null
  curl --retry 2 --retry-all-errors -fsSIL --max-time 20 https://services.gradle.org >/dev/null
  curl --retry 2 --retry-all-errors -fsSIL --max-time 20 https://dl.google.com >/dev/null
  printf '{"schema":"mbh-result-v1","status":"smoke-pass","source_sha":"%s","publish":false}\n' "$SOURCE_SHA" > .matrix-build-output/result.json
  exit 0
fi

if [ -f "$RECIPE_PATH" ]; then
  SCRIPT="$RECIPE_PATH"
  echo "MBH_RECIPE=repository:$RECIPE_PATH"
else
  SCRIPT="/tmp/matrix-build-fallback.sh"
  echo "MBH_RECIPE=central-fallback"
fi

chmod +x "$SCRIPT"
rm -f /tmp/mbh-build.log
set +e
MATRIX_REPO="$MATRIX_REPO" \
MATRIX_BRANCH="$BRANCH" \
MATRIX_SOURCE_SHA="$SOURCE_SHA" \
MATRIX_BUILD_ID="$BUILD_ID" \
timeout "${TIMEOUT_MINUTES}m" bash "$SCRIPT" > >(tee /tmp/mbh-build.log) 2>&1
rc=${PIPESTATUS[0]}
set -e

mkdir -p .matrix-build-output
cp /tmp/mbh-build.log .matrix-build-output/MBH_BUILD.log 2>/dev/null || true
printf '%s\n' "$rc" > .matrix-build-output/MBH_EXIT_CODE.txt
exit "$rc"
