#!/usr/bin/env bash
set -euo pipefail
remote=${1:-"https://github.com/leoLanxi/chineseVedioAnayls.git"}
git init
git add .
git commit -m "init"
git branch -M win11
git remote add origin "$remote" || true
git push -u origin win11
git checkout -b macos
git push -u origin macos

