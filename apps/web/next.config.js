/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: { appDir: true },
  output: 'standalone',
  transpilePackages: ['@dea/ui']
};

module.exports = nextConfig;
