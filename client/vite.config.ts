
import { defineConfig, loadEnv, type ConfigEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import fs from 'fs';
import path from 'path';

export default defineConfig(({ mode }: ConfigEnv) => {
  // load env vars for this mode
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react(), tailwindcss()],
    build: {
      target: "esnext", // <-- enables top-level await
    },
    // esbuild: {
    //   target: "esnext", // ✅ make esbuild output modern JS
    // },
    server: env.VITE_DEV === "true"
      ? {
          host: env.VITE_HOST,
          port: 5173,
          https: {
            key: fs.readFileSync(path.resolve(__dirname, `cert/${env.VITE_HOST}.key`)),
            cert: fs.readFileSync(path.resolve(__dirname, `cert/${env.VITE_HOST}.crt`)),
          },
          hmr: {
            protocol: 'wss',
            host: env.VITE_HOST,
            port: 5173,
          },
        }
      : undefined,
  };
});
