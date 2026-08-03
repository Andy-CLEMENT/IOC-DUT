#!/usr/bin/env bash
# Setup script for Linux / Jetson (arm64 or x64)
# Usage: chmod +x setup-linux.sh && ./setup-linux.sh
set -e

echo "== Fire Dashboard - Linux setup =="

if ! command -v node &> /dev/null; then
  echo "Node.js n'est pas installe. Installe-le d'abord (ex: sudo apt install nodejs npm, ou nvm)."
  exit 1
fi

echo "Node version: $(node -v)"
echo "npm version: $(npm -v)"

# Toujours repartir d'un node_modules propre : les binaires natifs
# (rolldown, tailwindcss oxide, lightningcss) sont specifiques a l'OS/arch.
# npm choisit automatiquement les bons binaires linux-x64 / linux-arm64
# grace aux "optionalDependencies" du package.json, a condition que
# l'install soit faite ICI, sur Linux, et pas copiee depuis Windows.
rm -rf node_modules package-lock.json

npm install

echo ""
echo "Installation terminee. Lancement du serveur de dev..."
npm run dev
