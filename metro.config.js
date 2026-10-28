const { getDefaultConfig } = require('expo/metro-config');
const { withDetectorProxy } = require('./scripts/detectorProxy.cjs');

const config = getDefaultConfig(__dirname);
const originalEnhancer = config.server.enhanceMiddleware;
config.server.enhanceMiddleware = (middleware, server) => withDetectorProxy(
  originalEnhancer ? originalEnhancer(middleware, server) : middleware,
);
module.exports = config;
