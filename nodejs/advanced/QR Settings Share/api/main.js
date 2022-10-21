let express = require('express');
let cors = require('cors')
var bodyParser = require('body-parser')

// Change to a different port to run locally. e.g. 8081
const port = 80;

let app = express();
app.use(cors())
app.use(bodyParser.json())

module.exports = app;

var distDir = __dirname + "/ui/"
app.use(express.static(distDir));

var localStore = {};

function checkDict(){
	
	var toDelete = [];
	for(var key in localStore) {
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
	for(var key in localStore) {
		var value = localStore[key];
		console.log("---------------");
		console.log("KEY=" + key);
		console.log("VALUE=" + value["value"]);
		console.log("expiry=" + value["expiry"]);
		console.log("---------------");
	}
}

app.post('/api', (req, res) => {
		
	console.log(req.body);
	
    var key = req.body.key;
    var value = req.body.value;
	console.log(value);
    var expiry = parseInt(req.body.expiry);
    localStore[key] = {"value": value, "expiry": expiry};
	
	checkDict();
	res.sendStatus(200);

})

app.get('/api/:key', (req, res) => {
	
	checkDict();
	
    var tokenDict = localStore[req.params.key];
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

app.listen(port, () => console.log(`Server running at http://127.0.0.1:${port}`))