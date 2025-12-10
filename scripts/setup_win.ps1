$ErrorActionPreference = "Stop"
$projectDir = (Resolve-Path "$PSScriptRoot\..\").Path
Set-Location $projectDir
$base = "D:\chineseVedioAnayls"
if (!(Test-Path $base)) { New-Item -ItemType Directory -Path $base | Out-Null }
$venvPath = Join-Path $base ".venv"
python - << 'PY'
import os,sys,venv
venv.EnvBuilder(with_pip=True).create(r'%s')
print('OK')
PY
$env:VIRTUAL_ENV = $venvPath
$env:PATH = "$venvPath\Scripts;" + $env:PATH
python -m pip install -r requirements.txt --upgrade
$tools = "D:\tools\ffmpeg"
if (!(Test-Path $tools)) { New-Item -ItemType Directory -Path $tools | Out-Null }
$zip = Join-Path $tools "ffmpeg.zip"
if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  $url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
  Invoke-WebRequest -Uri $url -OutFile $zip
  Expand-Archive -Path $zip -DestinationPath $tools -Force
  Remove-Item $zip
  $bin = Get-ChildItem -Directory $tools | Where-Object { Test-Path (Join-Path $_.FullName "bin\ffmpeg.exe") } | Select-Object -First 1
  if ($bin) { $env:PATH = (Join-Path $bin.FullName "bin") + ";" + $env:PATH }
}
$env:MODELSCOPE_CACHE = "D:\modelscope_cache"
if (!(Test-Path $env:MODELSCOPE_CACHE)) { New-Item -ItemType Directory -Path $env:MODELSCOPE_CACHE | Out-Null }
python scripts/prefetch_models.py
Write-Output "OK"

