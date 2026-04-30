import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_BASE_URL:
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://0.0.0.0:8000",
  },
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
