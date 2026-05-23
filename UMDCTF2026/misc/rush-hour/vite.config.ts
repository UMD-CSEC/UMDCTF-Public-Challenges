import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  publicDir: 'public',
  build: {
    target: 'es2015',
    outDir: 'dist',
  },
  server: {
    open: true,
    proxy: {
      '/ws': { target: 'ws://localhost:3000', ws: true },
    },
  },
});
