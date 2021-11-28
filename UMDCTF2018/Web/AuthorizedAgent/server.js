'use strict';

const express = require('express');
const path = require('path');

// Constants
const PORT = 3100;
const HOST = '0.0.0.0';
const app = express();

var _0x517a=['\x44\x65\x6e\x79\x20\x45\x76\x65\x72\x79\x74\x68\x69\x6e\x67\x3a\x20\x55\x4d\x44\x43\x54\x46\x2d\x7b\x73\x33\x63\x72\x33\x74\x5f\x40\x67\x33\x6e\x54\x5f\x6d\x40\x6e\x47\x7d\x0a'];var _0xa517=function(_0x5d6d13,_0x3689f4){_0x5d6d13=_0x5d6d13-0x0;var _0x5ee01b=_0x517a[_0x5d6d13];return _0x5ee01b;};var _0xf73e72=function(){var _0xa56d43=!![];return function(_0x33b9c7,_0xa72a1c){var _0x158b07=_0xa56d43?function(){if(_0xa72a1c){var _0x2648cd=_0xa72a1c['\x61\x70\x70\x6c\x79'](_0x33b9c7,arguments);_0xa72a1c=null;return _0x2648cd;}}:function(){};_0xa56d43=![];return _0x158b07;};}();var _0x2a935f=_0xf73e72(this,function(){var _0x47c8b7=function(){return'\x64\x65\x76';},_0x34785d=function(){return'\x77\x69\x6e\x64\x6f\x77';};var _0xac1bd=function(){var _0x3f65d9=new RegExp('\x5c\x77\x2b\x20\x2a\x5c\x28\x5c\x29\x20\x2a\x7b\x5c\x77\x2b\x20\x2a\x5b\x27\x7c\x22\x5d\x2e\x2b\x5b\x27\x7c\x22\x5d\x3b\x3f\x20\x2a\x7d');return!_0x3f65d9['\x74\x65\x73\x74'](_0x47c8b7['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var _0x5ce39a=function(){var _0x9e507b=new RegExp('\x28\x5c\x5c\x5b\x78\x7c\x75\x5d\x28\x5c\x77\x29\x7b\x32\x2c\x34\x7d\x29\x2b');return _0x9e507b['\x74\x65\x73\x74'](_0x34785d['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var _0x5f4bc5=function(_0x2bd386){var _0x337fe0=~-0x1>>0x1+0xff%0x0;if(_0x2bd386['\x69\x6e\x64\x65\x78\x4f\x66']('\x69'===_0x337fe0)){_0x46d6b8(_0x2bd386);}};var _0x46d6b8=function(_0x378d1c){var _0x2dae41=~-0x4>>0x1+0xff%0x0;if(_0x378d1c['\x69\x6e\x64\x65\x78\x4f\x66']((!![]+'')[0x3])!==_0x2dae41){_0x5f4bc5(_0x378d1c);}};if(!_0xac1bd()){if(!_0x5ce39a()){_0x5f4bc5('\x69\x6e\x64\u0435\x78\x4f\x66');}else{_0x5f4bc5('\x69\x6e\x64\x65\x78\x4f\x66');}}else{_0x5f4bc5('\x69\x6e\x64\u0435\x78\x4f\x66');}});_0x2a935f();_0xa517('0x0');
var _0xfc9d=['\x55\x73\x65\x72\x2d\x61\x67\x65\x6e\x74\x3a\x20\x42\x6c\x61\x63\x6b\x62\x65\x72\x72\x79\x20\x42\x6f\x6c\x64\x20\x39\x37\x38\x30\x0a\x44\x69\x73\x61\x6c\x6c\x6f\x77\x3a\x20\x66\x6c\x61\x67\x0a'];var _0xdfc9=function(_0x1336c7,_0x2c8622){_0x1336c7=_0x1336c7-0x0;var _0x2c9f11=_0xfc9d[_0x1336c7];return _0x2c9f11;};var _0x3d90e1=function(){var _0x3073f9=!![];return function(_0x124b3d,_0x88e0f7){var _0x4e0638=_0x3073f9?function(){if(_0x88e0f7){var _0x3ea415=_0x88e0f7['\x61\x70\x70\x6c\x79'](_0x124b3d,arguments);_0x88e0f7=null;return _0x3ea415;}}:function(){};_0x3073f9=![];return _0x4e0638;};}();var _0x432f01=_0x3d90e1(this,function(){var _0x3b59de=function(){return'\x64\x65\x76';},_0x38398a=function(){return'\x77\x69\x6e\x64\x6f\x77';};var _0x22f42e=function(){var _0xb341c0=new RegExp('\x5c\x77\x2b\x20\x2a\x5c\x28\x5c\x29\x20\x2a\x7b\x5c\x77\x2b\x20\x2a\x5b\x27\x7c\x22\x5d\x2e\x2b\x5b\x27\x7c\x22\x5d\x3b\x3f\x20\x2a\x7d');return!_0xb341c0['\x74\x65\x73\x74'](_0x3b59de['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var _0x3b5a80=function(){var _0x4fe265=new RegExp('\x28\x5c\x5c\x5b\x78\x7c\x75\x5d\x28\x5c\x77\x29\x7b\x32\x2c\x34\x7d\x29\x2b');return _0x4fe265['\x74\x65\x73\x74'](_0x38398a['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var _0x56a91a=function(_0x253b9e){var _0x375838=~-0x1>>0x1+0xff%0x0;if(_0x253b9e['\x69\x6e\x64\x65\x78\x4f\x66']('\x69'===_0x375838)){_0x2dfce0(_0x253b9e);}};var _0x2dfce0=function(_0x590a8b){var _0x192cce=~-0x4>>0x1+0xff%0x0;if(_0x590a8b['\x69\x6e\x64\x65\x78\x4f\x66']((!![]+'')[0x3])!==_0x192cce){_0x56a91a(_0x590a8b);}};if(!_0x22f42e()){if(!_0x3b5a80()){_0x56a91a('\x69\x6e\x64\u0435\x78\x4f\x66');}else{_0x56a91a('\x69\x6e\x64\x65\x78\x4f\x66');}}else{_0x56a91a('\x69\x6e\x64\u0435\x78\x4f\x66');}});_0x432f01();_0xdfc9('0x0');

app.use('/flag', function(req, res, next) {
    if (req.headers['user-agent'] != "Blackberry Bold 9780"){
        res.type('text/plain');
        res.send("Not authorized\nTry again Agent User");
    }
    else {
        res.type('text/plain');
        res.send(String(_0x517a));
    }
});

app.use(express.static(__dirname + '/view/'));

app.get('/', (req, res) => {
    // res.send();
    res.sendFile('index.html');
});

app.get('/flag', (req, res) => {
    // res.sendFile(path.join(__dirname + '/view/flag.html'))
    res.type('text/plain');
    res.send(req.headers['user-agent'])
});

app.get('/robots.txt', (req, res) => {
    res.type('text/plain');
    res.send(String(_0xfc9d));
});


app.listen(PORT, HOST);
console.log(`Runing on http://${HOST}:${PORT}`);
