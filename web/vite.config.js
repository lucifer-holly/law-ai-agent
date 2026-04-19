import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves this repo at https://<user>.github.io/legal-clause-index/
// so we need base: "/legal-clause-index/" in production builds. In dev we want
// the normal "/" root so `npm run dev` just works.
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === "production" ? "/law-ai-agent/" : "/",
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
  },
}));
