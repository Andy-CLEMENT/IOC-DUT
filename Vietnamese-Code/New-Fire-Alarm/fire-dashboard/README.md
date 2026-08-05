# Fire Dashboard

React dashboard (Vite + Tailwind CSS 4) for real-time visualization of fire/smoke alerts from the IOC system. Connects to the Jetson via WebSocket.

- **Path in repo:** `Vietnamese-Code/New-Fire-Alarm/fire-dashboard/`
- **WebSocket address to enter in the dashboard:** `ws://192.168.55.1:8765`

---

## Prerequisites

- [Node.js](https://nodejs.org/) v18 or later
- npm (installed with Node.js)

Check your versions:

```bash
node -v
npm -v
```

---

## Why setup differs between Windows and Linux

The `package.json` itself is identical on both OS — nothing to change in the code. The only pitfall: a few dependencies (`rolldown`, `@tailwindcss/oxide`, `lightningcss`) ship native binaries compiled for a specific OS. npm automatically picks the right one through `optionalDependencies`, **but only if `npm install` is run directly on the target machine.**

> **Never copy `node_modules` or transport it between Windows and Linux/Jetson** (zip, USB drive, shared folder, etc.). This is what causes the dashboard to work on one OS and crash on the other. Always reinstall locally on each machine.

---

## Setup — Linux / Jetson

```bash
cd ./IOC-DUT/Vietnamese-Code/New-Fire-Alarm/fire-dashboard
chmod +x setup-linux.sh
./setup-linux.sh
```

If you get `Permission denied` even after `chmod +x`, run it with bash directly instead:

```bash
bash setup-linux.sh
```

---

## Setup — Windows (PowerShell)

```powershell
cd .\IOC-DUT\Vietnamese-Code\New-Fire-Alarm\fire-dashboard
.\setup-windows.ps1
```

If PowerShell blocks the script with a `PSSecurityException` / `UnauthorizedAccess` error (scripts are blocked by default on Windows), run once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup-windows.ps1
```

If it's still blocked (file flagged as downloaded from the internet), unblock it first:

```powershell
Unblock-File .\setup-windows.ps1
.\setup-windows.ps1
```

---

## What the setup scripts do

Both `setup-linux.sh` and `setup-windows.ps1` do the same three things, just with OS-appropriate commands:

1. Check that Node.js/npm are installed
2. Remove any existing `node_modules` / `package-lock.json` and run a clean `npm install` (so npm fetches the binaries for the current OS)
3. Start the dev server with `npm run dev`

---

## Manual setup (equivalent, without the scripts)

```bash
cd Vietnamese-Code/New-Fire-Alarm/fire-dashboard
rm -rf node_modules package-lock.json   # Remove-Item -Recurse -Force node_modules, package-lock.json  (PowerShell)
npm install
npm run dev
```

---

## Production build

```bash
npm run build
```

Produces a static build in `dist/`, identical regardless of OS.

---

## Notes

- `node_modules/` and `package-lock.json` are in `.gitignore` — this is expected, they are regenerated locally on each install and should never be committed.
- Each team member (you, Andy, Alexis, DUT) runs their own `npm install` on their own machine after `git pull`.
- Once the dev server is running, open the dashboard in your browser and enter the WebSocket address `ws://192.168.55.1:8765` to connect to the Jetson.
