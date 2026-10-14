#!/usr/bin/env sh
# Builds dist/project-brainstorm.zip for upload to claude.ai.
set -e
cd "$(dirname "$0")/.."
mkdir -p dist
rm -f dist/project-brainstorm.zip
zip -rq dist/project-brainstorm.zip project-brainstorm
echo "Built dist/project-brainstorm.zip"
