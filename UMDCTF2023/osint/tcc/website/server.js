const fs = require("fs");
const https = require("https");
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 7000;
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname + '/public/'));

app.get(`/`, function(req, res) {
    res.sendFile(__dirname+'/index.html');
});

app.get(`/about`, function(req, res) {
    res.sendFile(__dirname+'/about.html');
});

app.get(`/contact`, function(req, res) {
    res.sendFile(__dirname+'/contact.html');
});

app.get(`/members`, function(req, res) {
    res.sendFile(__dirname+'/members.html');
});

app.get(`/secret`, function(req, res) {
    res.sendFile(__dirname+'/secret.html');
});

app.get(`/sitemap_092791284912.xml`, function(req, res) {
    res.status(200).sendFile(__dirname+'/sitemap_092791284912.xml');
});

app.post(`/secret`, function(req, res) {
    const a1 = req.body.a1;
    const a2 = req.body.a2;
    const a3 = req.body.a3;
    const a4 = req.body.a4;
    var count;

    //console.log(`Survey results: A1=${a1}, A2=${a2}, A3=${a3}, A4=${a4}`);
    count = (a1.trim() === "145") + (a2.toLowerCase().trim() === "leidos") + (a3.toLowerCase().trim() === "misc") + (a4.toLowerCase().trim() === "shazo");
    if (count == 4) {
	res.sendFile(__dirname+'/flag.html');
    } else {
	res.setHeader('correct-answers', `${count}`);
	//console.log(`You got ${count} correct...`);
	res.sendFile(__dirname+'/nope.html');
    }

    /*if (a1 === "145" && a2.toLowerCase() === "leidos" && a3.toLowerCase() === "misc" && a4.toLowerCase() === "shazo") {
	res.sendFile(__dirname+'/flag.html');
    } else {
	res.sendFile(__dirname+'/nope.html');
    } */
});

// HTTPS
/*const options = {
  key: fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.cert"),
};
https.createServer(options, app).listen(port, function (req, res) {
  console.log(`Server started at port ${port}`);
});  */

// HTTP
app.listen(port, () => console.log('Example app is listening on port ' + port +'.'));
