import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,       // ← ключевой момент: позволяет заходить извне (через Docker)
    port: 5173        // ← должен совпадать с портом в docker-compose
  }
});
