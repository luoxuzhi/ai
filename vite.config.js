import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/your-backend-endpoint': {
        target: 'http://localhost:5000', // 目标服务器地址
        changeOrigin: true, // 允许跨域
      },
    },
  },
})
