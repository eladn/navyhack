const express = require('express');
const bodyParser = require('body-parser')
const app = express();

// parse application/json
app.use(bodyParser.json());

const points = require('./API/points');
const entityData = require('./API/entityData');
const client = require('./client');

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.listen(3000, function () {
    console.log('App started');
});

app.use('/api/points', points);
app.use('/api/entity', entityData);
app.use('/', client);