// Development only: phones already reach Metro, so use that connection for
// uploads instead of requiring a second inbound port on the PC.
const http = require('node:http');

function withDetectorProxy(next) {
  return (request, response, nextMiddleware) => {
    const path = (request.url || '').split('?')[0];
    if (!path.startsWith('/timpla-detector/')) return next(request, response, nextMiddleware);
    const target = path.slice('/timpla-detector'.length);
    const sendError = (status, detail) => {
      if (response.destroyed || response.writableEnded) return;
      if (response.headersSent) { response.destroy(); return; }
      response.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
      response.end(JSON.stringify({ detail }));
    };
    if (!((request.method === 'GET' && target === '/health') ||
          (request.method === 'POST' && target === '/detect'))) {
      sendError(404, 'Detector route not found.'); return;
    }
    if (Number(request.headers['content-length']) > 5_100_000) {
      sendError(413, 'Photo must be 5 MB or smaller.'); return;
    }
    const headers = {};
    for (const name of ['content-type', 'content-length']) {
      if (request.headers[name]) headers[name] = request.headers[name];
    }
    const upstream = http.request({ hostname: '127.0.0.1', port: 8000,
      path: target, method: request.method, headers }, upstreamResponse => {
      response.writeHead(upstreamResponse.statusCode || 502, {
        'Content-Type': upstreamResponse.headers['content-type'] || 'application/json',
        'Cache-Control': 'no-store',
      });
      upstreamResponse.on('error', () => response.destroy());
      upstreamResponse.pipe(response);
    });
    upstream.setTimeout(125_000, () => upstream.destroy(Error('Detector timed out')));
    upstream.on('error', () => sendError(502,
      'The Python detector is unavailable on the PC. Start the detector service, then tap Retry.'));
    request.on('aborted', () => upstream.destroy());
    request.on('error', () => upstream.destroy());
    response.on('close', () => { if (!response.writableEnded) upstream.destroy(); });
    request.pipe(upstream);
  };
}

module.exports = { withDetectorProxy };
