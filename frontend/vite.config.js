import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { createRequire } from 'module';

var require = createRequire(import.meta.url);
var module = { exports: {} };

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/ask': 'http://localhost:8000',
      '/test-deals': 'http://localhost:8000',
      '/test-work-orders': 'http://localhost:8000',
      '/pipeline-summary': 'http://localhost:8000',
      '/pipeline-by-sector': 'http://localhost:8000',
      '/revenue-summary': 'http://localhost:8000',
      '/docs': 'http://localhost:8000',
      '/openapi.json': 'http://localhost:8000',
    },
  },
});
