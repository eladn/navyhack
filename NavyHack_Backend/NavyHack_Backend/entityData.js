const DB = require('./DB');
const express = require('express');

const router = express.Router();

function onDBError(err, res) {
    console.error(err);
    res.status(500);
    res.send('ERROR while getting point from db');
}

function onDBSuccess(res) {
    return function (err, points) {
        if (err) {
            onDBError(err, res);
        } else {
            res.json(points);
        }
    }
}

router.get('/:mmsi', function (req, res) {
    if (isNaN(parseInt(req.params.mmsi))) {
        res.status(403);
        return res.send(`mmsi ${req.params.mmsi} is invalid`);
    }

    console.log(`GET entity data for mmsi='${req.params.mmsi}'`);
    DB.entityData(req.params.mmsi, onDBSuccess(res));
});

module.exports = router;