'use strict';

// Credential-free TLS handshakes. A network error or expired test certificate is
// inconclusive and fails qualification; issuer distrust or revocation passes.
const tls = require('tls');
const fs = require('fs');
const path = require('path');

const fixtures = fs.readdirSync(path.join(__dirname, 'fixtures'))
  .filter(name => name.endsWith('.pem'))
  .map(name => name.slice(0, -4)).sort();
const issuerErrors = new Set([
  'CERT_REVOKED',
  'UNABLE_TO_GET_ISSUER_CERT_LOCALLY',
  'UNABLE_TO_VERIFY_LEAF_SIGNATURE',
  'SELF_SIGNED_CERT_IN_CHAIN',
]);

function handshake(host, mustReject) {
  return new Promise(resolve => {
    let finished = false;
    let socket;
    function finish(passed, result) {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      if (socket) socket.destroy();
      console.log(JSON.stringify({node: process.version, host, passed, result}));
      resolve(passed);
    }
    const timer = setTimeout(() => finish(false, 'TIMEOUT'), 15000);
    socket = tls.connect({host, servername: host, port: 443, rejectUnauthorized: true});
    socket.once('secureConnect', () => finish(!mustReject && socket.authorized,
      socket.authorized ? 'TLS_ACCEPTED' : 'TLS_NOT_AUTHORIZED'));
    socket.once('error', error => finish(mustReject && issuerErrors.has(error.code), error.code || 'ERROR'));
  });
}

Promise.resolve().then(function () {
  if (fixtures.length !== 12) {
    throw new Error('Exactly twelve certificate fixtures are required.');
  }
  return handshake('dev.azure.com', false).then(function (positive) {
    return Promise.all(fixtures.map(host => handshake(host, true))).then(function (negative) {
      process.exitCode = positive && negative.every(Boolean) ? 0 : 1;
    });
  });
}).catch(error => {
  console.error(error.message);
  process.exitCode = 2;
});
