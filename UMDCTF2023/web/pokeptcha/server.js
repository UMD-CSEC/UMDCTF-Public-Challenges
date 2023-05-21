const https = require("https");
const express = require('express');

const app = express();
const port = 6958;
app.use(express.static(__dirname + '/public/'));

app.get(`/`, function (req, res) {
    res.sendFile(__dirname + '/public');
});

app.listen(port, () => console.log('Listening on port', port));