# start-llm-router.ps1
param(
    [string]$ImageName     = "simongpt-llm-router",
    [string]$ContainerName = "llm-router",
    [string]$ApiKey        = "",
    [string]$OllamaUrl     = "http://host.docker.internal:11434",
    [int]   $Port          = 8080
)

Write-Host "⏳ Building Docker image '$ImageName'..."
docker build -t $ImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit 1
}

Write-Host "🛑 Stopping & removing any existing '$ContainerName' container..."
$existing = docker ps -a --filter "name=^$ContainerName$" --format "{{.ID}}"
if ($existing) {
    docker stop $ContainerName | Out-Null
    docker rm   $ContainerName | Out-Null
    Write-Host "➡️ Removed old container"
} else {
    Write-Host "⚠️ No existing container found"
}

Write-Host "🚀 Running new container '$ContainerName'..."
docker run -d `
    --name $ContainerName `
    -e "LLM_ROUTER_API_KEY=$ApiKey" `
    -e "OLLAMA_URL=$OllamaUrl" `
    -p ${Port}:$Port `
    $ImageName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start container"
    exit 1
}

Write-Host "✅ Container '$ContainerName' is up and listening on port $Port."