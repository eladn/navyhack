const DB = require('./DB');
const express = require('express');
const router = express.Router();

function onDBError(err, res) {
    console.error(err);
    res.status(500);
    res.send('ERROR while getting point from db');
}

router.post('/inextent', function (req, res) {
    console.log('GET points by extent');

    DB.pointsByExtent(req.body, function (err, points) {
        if (err) {
            onDBError(err, res);
        } else {
            res.json(points);
        }
    });
});

router.get('/inextent', function (req, res) {
    res.status(404);
});

router.get('/last', function (req, res) {
    console.log('GET last points');

    DB.lastPoints(function (err, points) {
        if (err) {
            onDBError(err, res);
        } else {
            res.json(points);
        }
    });
});

router.post('/last', function (req, res) {
    console.log('POST last points by extent');

    DB.lastPointsByExtent(req.body, function (err, points) {
        if (err) {
            onDBError(err, res);
        } else {
            res.json(points);
        }
    });
});

router.get('/:mmsi', function (req, res) {
    console.log('GET points by mmsi', req.params.mmsi);

    DB.pointsByMMSI(req.params.mmsi, function (err, points) {
        if (err) {
            onDBError(err, res);
        } else {
            res.json(points);
        }
    });
});

module.exports = router;