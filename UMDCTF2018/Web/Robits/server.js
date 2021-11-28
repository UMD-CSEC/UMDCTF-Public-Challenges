'use strict';

const express = require('express');
const path = require('path');

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';
const app = express();

app.use(express.static(__dirname + '/view/'));

app.get('/', (req, res) => {
    res.sendFile('index.html');
});

app.get('/8291ebebf9640a6d24c8a6894937270833f4ba7b2f8721236590f3b182c75505', (req, res) => {
    res.sendFile(path.join(__dirname + '/view/backdoor.html'));
});

app.get('/3976704ebabb2fb2e83e05bbd50955693ee41f5281eafc928c5d73ef2f59ff64', (req, res) => {
    res.sendFile(path.join(__dirname + '/view/flag.html'))
});

app.get('/robots.txt', (req, res) => {
    res.type('text/plain');
    res.send("User-agent: *\n" + 
    /* memes */"Disallow: 8291ebebf9640a6d24c8a6894937270833f4ba7b2f8721236590f3b182c75505\n" + 
    /* robits */"Disallow: 3976704ebabb2fb2e83e05bbd50955693ee41f5281eafc928c5d73ef2f59ff64\n");
});


app.listen(PORT, HOST)
console.log(`Runing on http://${HOST}:${PORT}`);
