﻿const EXTENT_WHERE = 'WHERE (?? BETWEEN ? AND ?) AND (?? BETWEEN ? AND ?)';

const GET_LAST_POINTS_QUERY = 'SELECT mmsi, lat, lon, class, course, speed, reported_time FROM ships_last_point_view';
const GET_POINTS_QUERY = "SELECT mmsi, lat, lon, class, course, speed, reported_time FROM ships_view";

const GET_POINTS_BY_COL_QUERY    = GET_POINTS_QUERY + " WHERE (?? = ?)";
const GET_POINTS_IN_EXTENT_QUERY = GET_POINTS_QUERY + " " + EXTENT_WHERE;
const GET_LAST_POINTS_IN_EXTENT_QUERY = GET_LAST_POINTS_QUERY + ' ' + EXTENT_WHERE;

const moment = require('moment');
const DB = {};

var mysql = require('mysql');
var pool = mysql.createPool({
    connectionLimit: 10,
    host: '192.168.1.150',
    user: 'navyhack',
    password: 'gidulter@',
    database: 'navyhack'
});

function rowToPoint(row) {
    // Convetr date to timestamp
    row.reported_time = +row.reported_time;

    return row;
}

DB.pointsByExtent = function (extent, cb) {
    var query = mysql.format(GET_POINTS_IN_EXTENT_QUERY, [
        'lat', extent.south, extent.north,
        'lon', extent.west, extent.east
    ]);

    pool.query(query, function (err, rows, fields) {
        if (err) return cb(err);

        var points = rows.map(rowToPoint);

        console.log('SELECT ended, rows:', rows.length);

        cb(null, points);
    });
};

DB.lastPointsByExtent = function (extent, cb) {
    var query = mysql.format(GET_LAST_POINTS_IN_EXTENT_QUERY, [
        'lat', extent.south, extent.north,
        'lon', extent.west, extent.east
    ]);

    pool.query(query, function (err, rows, fields) {
        if (err) return cb(err);

        var points = rows.map(rowToPoint);

        console.log('SELECT ended, rows:', rows.length);

        cb(null, points);
    });
};

DB.pointsByMMSI = function (mmsi,cb) {
    var query = mysql.format(GET_POINTS_BY_COL_QUERY, [
        'mmsi', mmsi
    ]);

    pool.query(query, function (err, rows, fields) {
        if (err) return cb(err);

        var points = rows.map(rowToPoint);

        console.log('SELECT ended, rows:', rows.length);

        cb(null, points);
    });
};

DB.lastPoints = function (cb) {
    var query = mysql.format(GET_LAST_POINTS_QUERY);

    pool.query(query, function (err, rows, fields) {
        if (err) return cb(err);

        var points = rows.map(rowToPoint);

        console.log('SELECT ended, rows:', rows.length);

        cb(null, points);
    });
};

module.exports = DB;