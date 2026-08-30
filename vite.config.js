import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  server: {
    port: 5173,
    host: true,
  open: false,
  // Proxy /predict to local FastAPI when running locally;
  // in Bolt preview the backend isn't running, so the fetch will fail
  // and the UI will show a graceful preview-mode message.
    proxy: {
      '/predict': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
});
