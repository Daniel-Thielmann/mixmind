import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const parsedApiUrl = new URL(apiUrl);

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: parsedApiUrl.protocol.replace(":", "") as "http" | "https",
        hostname: parsedApiUrl.hostname,
        port: parsedApiUrl.port,
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;
