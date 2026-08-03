# Setup script for Windows
# Usage: click-right > "Run with PowerShell", or in a PowerShell terminal:
#   .\setup-windows.ps1
# If execution is blocked, run once: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Write-Host "== Fire Dashboard - Windows setup =="

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js n'est pas installe. Telecharge-le sur https://nodejs.org/"
    exit 1
}

Write-Host "Node version: $(node -v)"
Write-Host "npm version: $(npm -v)"

# Toujours repartir d'un node_modules propre : les binaires natifs
# (rolldown, tailwindcss oxide, lightningcss) sont specifiques a l'OS.
# npm choisit automatiquement les binaires win32-x64 grace aux
# "optionalDependencies" du package.json, a condition que l'install
# soit faite ICI, sous Windows, et pas copiee depuis Linux.
if (Test-Path node_modules) { Remove-Item -Recurse -Force node_modules }
if (Test-Path package-lock.json) { Remove-Item -Force package-lock.json }

npm install

Write-Host ""
Write-Host "Installation terminee. Lancement du serveur de dev..."
npm run dev
