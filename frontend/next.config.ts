import type { NextConfig } from "next";

/**
 * Next.js configuration.
 *
 * `images.remotePatterns` whitelists the hosts we load optimized images from:
 * the Django backend (menu item photos) in dev, and the production API host.
 * The API host is supplied via NEXT_PUBLIC_IMAGE_HOST at build time.
 */
const imageHost = process.env.NEXT_PUBLIC_IMAGE_HOST;

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
      // Production backend host (e.g. your-api.onrender.com), if configured.
      ...(imageHost
        ? [
            {
              protocol: "https" as const,
              hostname: imageHost,
              pathname: "/media/**",
            },
          ]
        : []),
    ],
  },
};

export default nextConfig;
