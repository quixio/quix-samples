let express = require('express');
let cors = require('cors')
const bodyParser = require('body-parser');
const https = require('https');
const http = require('http');
const fs = require('fs');

const path = require('path');

let app = express();

app.use(cors())
app.use(bodyParser.json())

module.exports = app;

const distDir = __dirname + "/ui/";
app.use(express.static(distDir));

const localStore = {};

function checkDict(){

	const toDelete = [];
	for(let key in localStore) {
		var value = localStore[key];
		
		console.log(Date.now());
		console.log(value["expiry"]);
		console.log(value["expiry"] < Date.now());
		
		if(value["expiry"] < Date.now()){
			toDelete.push(key);
		}
	}
	toDelete.forEach(myFunction);

	function myFunction(value, index, array) {
	  delete localStore[value];
	  console.log("Deleted " + value);
	}
	
	debug();
}

function debug(){
	console.log("DEBUG");
	for(let key in localStore) {
		const value = localStore[key];
		console.log("---------------");
		console.log("KEY=" + key);
		console.log("VALUE=" + value["value"]);
		console.log("expiry=" + value["expiry"]);
		console.log("---------------");
	}
}

// support the UI
function read_file(file, res){
	fs.readFile('/my-app/api/' + file, 'utf8', (err, data) => {
		if (err) {
			console.error(err);
			res.status(404).send("Error. See console log");
			return;
		}
		let value = data.replace(/(\r\n|\n|\r)/gm, "");
		console.log(value);
		res.status(200).send(value);
	});
}

app.get('/api/bearer_token', (req, res) => {
	read_file("bearer_token", res);
});
app.get('/api/portal_api', (req, res) => {
	read_file("portal_api", res);
});
app.get('/api/workspace_id', (req, res) => {
	read_file("workspace_id", res);
})

app.post('/api', (req, res) => {
		
	console.log(req.body);

	const key = req.body.key;
	const value = req.body.value;
	console.log(value);
	const expiry = parseInt(req.body.expiry);
	localStore[key] = {"value": value, "expiry": expiry};
	
	checkDict();
	res.sendStatus(200);

})

app.get('/api/:key', (req, res) => {
	
	checkDict();

	const tokenDict = localStore[req.params.key];
	if(tokenDict !== undefined){
		res.send(tokenDict.value);
	}
	else{
		res.status(404).send("Sorry can't find that!");
	}
})

app.get('/heartbeat', (req, res) => {
    res.status(200).send("ALL GOOD HERE!");
})

console.log("Listening on port 80");

let httpServer = http.createServer(app);
httpServer.listen(80);