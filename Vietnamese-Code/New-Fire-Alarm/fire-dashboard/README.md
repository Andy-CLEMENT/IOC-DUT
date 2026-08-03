# Fire Dashboard

Dashboard React + Vite + Tailwind CSS 4 pour le systeme de detection incendie/fumee IOC.

## Installation

Le `package.json` est le meme pour Windows et Linux : aucune config a dupliquer dans le
code. Le seul piege, c'est que certaines dependances (`rolldown`, `@tailwindcss/oxide`,
`lightningcss`) embarquent des binaires natifs compiles pour un OS precis. npm sait choisir
automatiquement la bonne version grace aux `optionalDependencies`, **mais seulement si
`npm install` est execute directement sur la machine cible** — jamais en copiant un
`node_modules` d'un OS vers un autre.

C'est pour ca qu'il y a deux scripts, un par OS, qui font chacun un install propre puis
lancent le serveur de dev :

### Sous Linux / Jetson

```bash
chmod +x setup-linux.sh
./setup-linux.sh
```

### Sous Windows (PowerShell)

```powershell
.\setup-windows.ps1
```

(Si l'execution de scripts est bloquee : `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` une fois, puis relancer.)

## Commandes manuelles

Si tu preferes le faire a la main (equivalent a ce que font les scripts) :

```bash
rm -rf node_modules package-lock.json   # Remove-Item sous PowerShell
npm install
npm run dev
```

## Notes

- Chaque OS doit faire son propre `npm install` : ne jamais transporter `node_modules`
  ou `package-lock.json` d'un Windows vers un Linux (ou l'inverse) via zip/clé USB/etc.
- `node_modules/` et `package-lock.json` sont dans le `.gitignore` : normal, ils sont
  regeneres localement a chaque install.
- `npm run build` genere le build de production dans `dist/`, identique quel que soit l'OS.
