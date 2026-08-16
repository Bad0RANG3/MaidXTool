const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const PORT = Number(process.env.PORT || 8787);
const SDGB_DIR = path.join(ROOT, '..', 'sdgb');
const RUNNER_SCRIPT = path.join(ROOT, 'run_qr.py');
const DECODED_FILE = path.join(ROOT, 'decoded_qr.txt');
const LOG_FILE = path.join(ROOT, 'decoded_qr.log');
const ECHO_MODE = process.env.QR_RUNNER === 'echo';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

function log(msg) { console.log(`[${new Date().toISOString()}] ${msg}`); }

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', c => { data += c; if (data.length > 1e6) req.destroy(); });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, urlPath);
  if (!filePath.startsWith(ROOT)) { res.writeHead(403); res.end('forbidden'); return; }
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not Found'); return; }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

function runQrApi(text) {
  return new Promise((resolve) => {
    if (ECHO_MODE) {
      resolve({ ok: true, result: { echo: text, note: 'QR_RUNNER=echo 测试模式，未实际调用 qr_api' } });
      return;
    }
    const args = [RUNNER_SCRIPT, text];
    const child = spawn('python', args, { cwd: SDGB_DIR, windowsHide: true });
    let out = '', err = '';
    const timer = setTimeout(() => { child.kill(); }, 25000);
    child.stdout.on('data', d => { out += d; });
    child.stderr.on('data', d => { err += d; });
    child.on('close', code => {
      clearTimeout(timer);
      let parsed = null;
      const start = out.indexOf('{');
      const end = out.lastIndexOf('}');
      if (start !== -1 && end > start) {
        try { parsed = JSON.parse(out.slice(start, end + 1)); } catch (_) { /* ignore */ }
      }
      if (parsed && typeof parsed.ok === 'boolean') {
        resolve(parsed);
      } else {
        resolve({ ok: false, error: `python 退出码 ${code}`, detail: (out + err).slice(-2000) });
      }
    });
    child.on('error', e => {
      clearTimeout(timer);
      resolve({ ok: false, error: `无法启动 python: ${e.message}` });
    });
  });
}

async function handleApi(req, res) {
  const url = req.url.split('?')[0];

  if (req.method === 'GET' && url === '/api/last') {
    let last = '';
    try { last = fs.readFileSync(DECODED_FILE, 'utf8'); } catch (_) { /* no file yet */ }
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ last }));
    return;
  }

  if (req.method === 'POST' && url === '/api/qr') {
    let body;
    try { body = JSON.parse(await readBody(req)); } catch (_) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: '请求体不是合法 JSON' }));
      return;
    }
    const text = String(body.text || '').trim();
    if (!text) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: '解析结果为空' }));
      return;
    }

    fs.writeFileSync(DECODED_FILE, text, 'utf8');
    log(`收到二维码字符串(${text.length} 字符): ${text.slice(0, 20)}…`);

    const result = await runQrApi(text);
    const line = `${new Date().toISOString()} len=${text.length} ok=${result.ok} ${result.error || JSON.stringify(result.result || {}).slice(0, 200)}`;
    fs.appendFileSync(LOG_FILE, line + '\n', 'utf8');
    log(`qr_api 返回 ok=${result.ok}`);

    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ ok: result.ok, result: result.result, error: result.error, detail: result.detail }));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ ok: false, error: 'Not Found' }));
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith('/api/')) {
    handleApi(req, res).catch(e => {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: String(e) }));
    });
  } else {
    serveStatic(req, res);
  }
});

server.listen(PORT, '127.0.0.1', () => {
  log(`QR 服务已启动: http://127.0.0.1:${PORT}  (QR_RUNNER=${ECHO_MODE ? 'echo(测试)' : 'python(调用 qr_api)'})`);
});

