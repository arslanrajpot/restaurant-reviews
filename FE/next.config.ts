// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['reviewmunch.com'], // ✅ allow external image domain
  },
};

module.exports = nextConfig;
