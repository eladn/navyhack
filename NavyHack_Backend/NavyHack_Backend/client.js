const path = require('path');
const express = require('express');
const router = express.Router();

router.use('/scripts', express.static(path.join(__dirname,'node_modules')));
router.use('/client/res', express.static(path.join(__dirname,'client')));

router.get('/', function (req, res) {
    console.log(`GET index.html`);
    res.sendFile(path.join(__dirname,'Client','index.html'));
});

module.exports = router;