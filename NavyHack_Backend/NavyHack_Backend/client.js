const path = require('path');
const express = require('express');
const router = express.Router();

router.use('/scripts',    express.static(`${__dirname}/node_modules/`));
router.use('/client/res', express.static(`${__dirname}/client`));

router.get('/', function (req, res) {
    console.log(`GET index.html`);
    res.sendFile(`${__dirname}/client/index.html`);
});

module.exports = router;