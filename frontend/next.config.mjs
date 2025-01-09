/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "standalone",
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'assets.aceternity.com',
                pathname: '**'
            },
            {
                protocol: 'https',
                hostname: 'nextui.org',
                pathname: '**'
            }
        ]
    }
};

export default nextConfig;
