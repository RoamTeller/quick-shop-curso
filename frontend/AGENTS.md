# Frontend
- Respetar AGENTS.md de la raíz.
- React Router y cliente API centralizado. Tokens solo en memoria, nunca localStorage ni sessionStorage.
- Interfaz responsive, accesible y en castellano; tratar cargas y errores visibles.
- Los formularios deben impedir envíos duplicados y mantener la información si falla la API.
- Configurar PostCSS inline en vite.config.js solo con tailwindcss(); no añadir autoprefixer externo.
- pnpm 11: aprobaciones de scripts mediante allowBuilds en pnpm-workspace.yaml, no en el lockfile. Docker debe copiar ese archivo antes de instalar.
