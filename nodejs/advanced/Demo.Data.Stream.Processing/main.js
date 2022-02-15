let express = require('express');
let cors = require('cors')
let resultUtil = require("./js/result")

// Change to a different port to run locally. e.g. 8081
const port = 80;

let app = express();
app.use(cors())

module.exports = app;

app.use('/images', express.static(__dirname + '/images'));

app.use('/css', express.static('css'));
app.use('/js', express.static('js'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + "/landing-page.html");
})

app.get('/start', (req, res) => {
    res.sendFile(__dirname + "/create.html");
})

app.get('/play', (req, res) => {
    res.sendFile(__dirname + "/phone.html");
})

app.get('/result/:streamId', (req, res) => {
    resultUtil.getGameResult(req.params.streamId, data => {
        let rtn = { dataPoints: data.dataPoints }
        res.send(JSON.stringify(rtn));
    });
})

app.listen(port, () => console.log(`Server running at http://127.0.0.1:${port}`))