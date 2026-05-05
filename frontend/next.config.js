/** @type {import('next').NextConfig} */
module.exports = {
  output: 'standalone',
  reactStrictMode: true,
  // Let the dev server proxy NASA images and our backend's /media/ URLs.
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "apod.nasa.gov" },
      { protocol: "https", hostname: "**.nasa.gov" },
      { protocol: "http", hostname: "localhost" },
    ],
  },
};
