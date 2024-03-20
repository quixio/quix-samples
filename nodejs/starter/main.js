var express = require('express');

const port = 80;

var app = express();

module.exports = app;

app.use('/css', express.static('css'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + "/index.html");
})
app.listen(port, () => console.log(`Server running at http://127.0.0.1:${port}`))
