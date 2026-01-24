import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import frappeui from 'frappe-ui/vite'
import path from 'path'
// https://vite.dev/config/
export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      lucideIcons: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: '../referralpro/www/rp.html',
        emptyOutDir: true,
        sourcemap: true,
      },

    }),
    vue(),
    vueDevTools(),
    {
      name: 'transform-index.html',
      transformIndexHtml(html, context) {
        if (!context.server) {
          return html.replace(
            /<\/body>/,
            `
            <script>
                {% for key in boot %}
                window["{{ key }}"] = {{ boot[key] | tojson }};
                {% endfor %}
            </script>
            </body>
            `
          )
        }
        return html
      },
    },

  ],
  server: {
    host: '0.0.0.0',
    port: 8080,
    hmr: {
      overlay: false
    },
    watch: {
      usePolling: true
    },
    allowedHosts: ['localdev.sophiecore.com'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'tailwind.config.js': path.resolve(__dirname, 'tailwind.config.js'),
    },
  },
  optimizeDeps: { include: ['debug', 'frappe-ui > feather-icons', 'showdown', 'engine.io-client', 'lowlight', 'interactjs'], },
  build: {
    // target:"ES2022",
    rollupOptions: {
      treeshake: false
    },
    outDir: `../referralpro/public/frontend`,
    emptyOutDir: true,
    commonjsOptions: {
      include: [/tailwind.config.js/, /node_modules/],
    },
    sourcemap: true,
  }

})
