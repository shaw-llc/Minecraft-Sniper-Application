import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: path.resolve(__dirname, 'src/renderer'),
  build: {
    outDir: path.resolve(__dirname, 'dist'),
    emptyOutDir: true,
  },
  server: {
    port: 3000
  }
}); 