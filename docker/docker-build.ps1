param(
    [string]$Version = "1.1.2c",
    [string]$Username = "doalou"
)

$ImageName = "toolbox-everything"
$FullImage = "$Username/$ImageName"

Write-Host "🚀 Building Docker image for Docker Hub" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📦 Image: $FullImage" -ForegroundColor Yellow
Write-Host "🏷️  Version: $Version" -ForegroundColor Yellow  
Write-Host "👤 Username: $Username" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker non accessible"
    }
} catch {
    Write-Host "❌ Erreur: Docker n'est pas en cours d'exécution" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host "🔨 Building image..." -ForegroundColor Blue
docker build `
    --tag "$FullImage`:latest" `
    --tag "$FullImage`:$Version" `
    --tag "$FullImage`:v$Version" `
    .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Échec du build" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build terminé avec succès!" -ForegroundColor Green

Write-Host "📋 Images créées:" -ForegroundColor Cyan
docker images $FullImage

$response = Read-Host "🤔 Voulez-vous push les images vers Docker Hub? (y/N)"
if ($response -match "^[Yy]$") {
    Write-Host "📤 Pushing images to Docker Hub..." -ForegroundColor Blue
    
    Write-Host "🔐 Vérification de la connexion Docker Hub..." -ForegroundColor Yellow
    $dockerInfo = docker info 2>$null
    if (-not ($dockerInfo -match "Username")) {
        Write-Host "🔑 Connexion à Docker Hub requise:" -ForegroundColor Yellow
        docker login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Échec de la connexion" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "⬆️  Pushing $FullImage`:latest..." -ForegroundColor Blue
    docker push "$FullImage`:latest"
    
    Write-Host "⬆️  Pushing $FullImage`:$Version..." -ForegroundColor Blue
    docker push "$FullImage`:$Version"
    
    Write-Host "⬆️  Pushing $FullImage`:v$Version..." -ForegroundColor Blue
    docker push "$FullImage`:v$Version"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🎉 Push terminé avec succès!" -ForegroundColor Green
        Write-Host "🌐 Votre image est maintenant disponible sur:" -ForegroundColor Cyan
        Write-Host "   https://hub.docker.com/r/$Username/$ImageName" -ForegroundColor White
    } else {
        Write-Host "❌ Échec du push" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⏸️  Push annulé. Vous pouvez push manuellement avec:" -ForegroundColor Yellow
    Write-Host "   docker push $FullImage`:latest" -ForegroundColor White
    Write-Host "   docker push $FullImage`:$Version" -ForegroundColor White
}

Write-Host "✨ Terminé!" -ForegroundColor Green 