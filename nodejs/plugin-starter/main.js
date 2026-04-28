const express = require('express');
const path = require('path');

const port = process.env.PORT || 80;
const app = express();

app.use(express.static(path.join(__dirname, 'public')));

app.get('/healthz', (_req, res) => res.send('ok'));

app.listen(port, () => {
  console.log(`Plugin starter listening on http://0.0.0.0:${port}`);
});
