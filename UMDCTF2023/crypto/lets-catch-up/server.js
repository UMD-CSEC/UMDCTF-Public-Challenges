const https = require("https");
const express = require('express');

const app = express();
const port = 6958;
app.use(express.static(__dirname + '/public/'));

app.get(`/`, function(req, res) {
    res.sendFile(__dirname+'/index.html');
});

/*const options = {
  key: fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.cert"),
};

https.createServer(options, app).listen(port, function (req, res) {
  console.log(`Server started at port ${port}`);
});

*/

// HTTP
app.listen(port, () => console.log('Listening on port', port));
