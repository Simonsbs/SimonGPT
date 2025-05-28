<#
.SYNOPSIS
  Build and run the Watcher service in Docker, stopping any existing container.

.DESCRIPTION
  - Reads configuration from .env
  - Builds the Docker image from the local Dockerfile
  - Stops & removes any existing container with the given name
  - Runs a new container, passing through all required env vars
  - Mounts your host watch folder into the container

.PARAMETER ImageName
  Name for the built Docker image (default: simongpt-watcher).

.PARAMETER ContainerName
  Name for the running container (default: watcher).

.PARAMETER HostWatchDir
  Absolute host folder path to watch. Default: "$PSScriptRoot\watched".
#>

param(
  [string]$ImageName      = "simongpt-watcher",
  [string]$ContainerName  = "watcher",
  [string]$HostWatchDir   = "$PSScriptRoot\watched"
)

# 1) Load .env values into PS variables if not already set
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
  Write-Host "🔍 Loading .env..."
  foreach ($line in Get-Content $envFile) {
    if ($line -match '^\s*([^#=]+)\s*=\s*(.*)$') {
      $key = $matches[1].Trim()
      $val = $matches[2].Trim('"')
      if (-not (Get-Variable -Name $key -Scope Local -ErrorAction SilentlyContinue)) {
        Set-Variable -Name $key -Value $val
      }
    }
  }
}

# 2) Validate required env vars
foreach ($var in @("VECTOR_DB_URL","ROUTER_URL","ROUTER_API_KEY","EMBED_MODEL","WATCH_DIR")) {
  if (-not (Get-Variable -Name $var -Scope Local -ErrorAction SilentlyContinue)) {
    Write-Error "$var is not defined in .env or parameters."
    exit 1
  }
}

# 3) Ensure host watch directory exists
if (-not (Test-Path $HostWatchDir)) {
  Write-Host "📂 Creating host watch directory: $HostWatchDir"
  New-Item -ItemType Directory -Path $HostWatchDir | Out-Null
}

Write-Host "🚧 Mounting host [$HostWatchDir] → container [$WATCH_DIR]"

# 4) Build Docker image
Write-Host "⏳ Building Docker image '$ImageName'..."
docker build -t $ImageName . 
if ($LASTEXITCODE -ne 0) {
  Write-Error "❌ Build failed"
  exit 1
}

# 5) Stop & remove existing container
Write-Host "🛑 Removing old container '$ContainerName' if exists..."
$old = docker ps -a --filter "name=^$ContainerName$" --format "{{.ID}}"
if ($old) {
  docker stop $ContainerName | Out-Null
  docker rm   $ContainerName | Out-Null
  Write-Host "➡️ Removed existing container"
} else {
  Write-Host "⚠️ No existing container found"
}

# 6) Run the new container
Write-Host "🚀 Starting container '$ContainerName'..."
docker run -d `
  --name $ContainerName `
  -e "VECTOR_DB_URL=$VECTOR_DB_URL" `
  -e "ROUTER_URL=$ROUTER_URL" `
  -e "ROUTER_API_KEY=$ROUTER_API_KEY" `
  -e "EMBED_MODEL=$EMBED_MODEL" `
  -e "WATCH_DIR=$WATCH_DIR" `
  -v "${HostWatchDir}:${WATCH_DIR}" `
  $ImageName

if ($LASTEXITCODE -ne 0) {
  Write-Error "❌ Failed to start container"
  exit 1
}

Write-Host "✅ Container '$ContainerName' is running and watching '$WATCH_DIR'."
