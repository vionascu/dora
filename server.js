#!/usr/bin/env node
/**
 * DORA Metrics Dashboard - Development Server
 * Serves the dashboard and exposes calculation data
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;
const ROOT_DIR = __dirname;

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  const parsedUrl = url.parse(req.url, true);
  let pathname = decodeURI(parsedUrl.pathname);

  // API endpoint for serving calculation data
  if (pathname.startsWith('/api/')) {
    const dataPath = pathname.slice(5); // Remove /api/
    const fullPath = path.join(ROOT_DIR, dataPath);

    // Security: prevent directory traversal
    if (!fullPath.startsWith(ROOT_DIR)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    fs.readFile(fullPath, (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));
      } else {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(data);
      }
    });
    return;
  }

  // Serve static files
  if (pathname === '/') {
    pathname = '/index.html';
  }

  let filePath = path.join(ROOT_DIR, 'public', pathname);

  // Security: prevent directory traversal
  if (!filePath.startsWith(path.join(ROOT_DIR, 'public'))) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 - Not Found</h1>');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = mimeTypes[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('DORA Metrics Dashboard Server');
  console.log('='.repeat(60));
  console.log(`\n✓ Server running at http://localhost:${PORT}`);
  console.log('\nAPI Endpoints:');
  console.log(`  • http://localhost:${PORT}/api/calculations/global/summary.json`);
  console.log(`  • http://localhost:${PORT}/api/calculations/per_repo/[repo]/commits.json`);
  console.log('\nPress Ctrl+C to stop\n');
});
