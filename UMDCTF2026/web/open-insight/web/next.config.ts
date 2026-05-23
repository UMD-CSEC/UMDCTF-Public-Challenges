import type { NextConfig } from "next";

const config: NextConfig = {
  serverExternalPackages: ["better-sqlite3"],
  productionBrowserSourceMaps: false,

  
};

export default config;
