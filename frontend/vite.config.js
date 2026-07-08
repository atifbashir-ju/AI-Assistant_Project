import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Reads the backend URL from an env var so it's configurable per-environment
// (see .env.example). Falls back to localhost for local dev.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
