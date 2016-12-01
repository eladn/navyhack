var map,
    shuldPaintAllInSameColor = true;

function initMap() {

    var styledMapType = new google.maps.StyledMapType(
        [{ "featureType": "all", "elementType": "all", "stylers": [{ "visibility": "on" }] }, { "featureType": "all", "elementType": "labels", "stylers": [{ "visibility": "off" }, { "saturation": "-100" }] }, { "featureType": "all", "elementType": "labels.text.fill", "stylers": [{ "saturation": 36 }, { "color": "#000000" }, { "lightness": 40 }, { "visibility": "off" }] }, { "featureType": "all", "elementType": "labels.text.stroke", "stylers": [{ "visibility": "off" }, { "color": "#000000" }, { "lightness": 16 }] }, { "featureType": "all", "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] }, { "featureType": "administrative", "elementType": "geometry.fill", "stylers": [{ "color": "#000000" }, { "lightness": 20 }] }, { "featureType": "administrative", "elementType": "geometry.stroke", "stylers": [{ "color": "#000000" }, { "lightness": 17 }, { "weight": 1.2 }] }, { "featureType": "landscape", "elementType": "geometry", "stylers": [{ "color": "#000000" }, { "lightness": 20 }] }, { "featureType": "landscape", "elementType": "geometry.fill", "stylers": [{ "color": "#4d6059" }] }, { "featureType": "landscape", "elementType": "geometry.stroke", "stylers": [{ "color": "#4d6059" }] }, { "featureType": "landscape.natural", "elementType": "geometry.fill", "stylers": [{ "color": "#4d6059" }] }, { "featureType": "poi", "elementType": "geometry", "stylers": [{ "lightness": 21 }] }, { "featureType": "poi", "elementType": "geometry.fill", "stylers": [{ "color": "#4d6059" }] }, { "featureType": "poi", "elementType": "geometry.stroke", "stylers": [{ "color": "#4d6059" }] }, { "featureType": "road", "elementType": "geometry", "stylers": [{ "visibility": "on" }, { "color": "#7f8d89" }] }, { "featureType": "road", "elementType": "geometry.fill", "stylers": [{ "color": "#7f8d89" }] }, { "featureType": "road.highway", "elementType": "geometry.fill", "stylers": [{ "color": "#7f8d89" }, { "lightness": 17 }] }, { "featureType": "road.highway", "elementType": "geometry.stroke", "stylers": [{ "color": "#7f8d89" }, { "lightness": 29 }, { "weight": 0.2 }] }, { "featureType": "road.arterial", "elementType": "geometry", "stylers": [{ "color": "#000000" }, { "lightness": 18 }] }, { "featureType": "road.arterial", "elementType": "geometry.fill", "stylers": [{ "color": "#7f8d89" }] }, { "featureType": "road.arterial", "elementType": "geometry.stroke", "stylers": [{ "color": "#7f8d89" }] }, { "featureType": "road.local", "elementType": "geometry", "stylers": [{ "color": "#000000" }, { "lightness": 16 }] }, { "featureType": "road.local", "elementType": "geometry.fill", "stylers": [{ "color": "#7f8d89" }] }, { "featureType": "road.local", "elementType": "geometry.stroke", "stylers": [{ "color": "#7f8d89" }] }, { "featureType": "transit", "elementType": "geometry", "stylers": [{ "color": "#000000" }, { "lightness": 19 }] }, { "featureType": "water", "elementType": "all", "stylers": [{ "color": "#2b3638" }, { "visibility": "on" }] }, { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#2b3638" }, { "lightness": 17 }] }, { "featureType": "water", "elementType": "geometry.fill", "stylers": [{ "color": "#24282b" }] }, { "featureType": "water", "elementType": "geometry.stroke", "stylers": [{ "color": "#24282b" }] }, { "featureType": "water", "elementType": "labels", "stylers": [{ "visibility": "off" }] }, { "featureType": "water", "elementType": "labels.text", "stylers": [{ "visibility": "off" }] }, { "featureType": "water", "elementType": "labels.text.fill", "stylers": [{ "visibility": "off" }] }, { "featureType": "water", "elementType": "labels.text.stroke", "stylers": [{ "visibility": "off" }] }, { "featureType": "water", "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] }],
        { name: 'Styled Map' });

    // Create a map object, and include the MapTypeId to add
    // to the map type control.
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 32.7940, lng: 34.9896 },
        zoom: 9,
        mapTypeControlOptions: {
            mapTypeIds: ['styled_map']
        },
        disableDefaultUI: true
    });

    //Associate the styled map with the MapTypeId and set it to display.
    map.mapTypes.set('styled_map', styledMapType);
    map.setMapTypeId('styled_map');

    // Fetch all ships
    fetchData(map.getBounds());


    google.maps.event.addListener(map, 'bounds_changed', function () {
 
        fetchData(map.getBounds());
    });
}

////////////////////////////////// Fetch points of ship ///////////////////////

var allShips = [];
var historyDrawings = {};

function fetchPointsOfShip(mmsi) {
    $.getJSON('/api/points/' + mmsi, function (response) {

        drawShipHistory(response, mmsi);
    });
}

function drawShipHistory(points, mmsi) {
    points.sort(function (a, b) {

        return a.reported_time - b.reported_time;
    });

    // Remove the last point - latest time (because we already have it on the map)
    points.pop();


    historyDrawings[mmsi] = [];

    var shipPlanCoordinates = [];
    for (var i = 0; i < points.length; i++) {

        var point = points[i];

        var currentCoordinates = { lat: point.lat, lng: point.lon };

        shipPlanCoordinates.push(currentCoordinates);

        var marker = new google.maps.Marker({
            position: currentCoordinates,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                strokeWeight: 2,
                fillColor: shipTypeToColor(allShips[mmsi].class),
                strokeColor: shipTypeToColor(allShips[mmsi].class),
                scale: 4,
            }
        });

        marker.shipType = allShips[mmsi].class;

        historyDrawings[mmsi].push(marker);

        addToMap(marker);
    }

    // Add the ship's last location for line drawing
    shipPlanCoordinates.push({ lat: allShips[mmsi].lat, lng: allShips[mmsi].lon });

    var line = new google.maps.Polyline({
        path: shipPlanCoordinates,
        strokeColor: shipTypeToColor(allShips[mmsi].class),
        strokeOpacity: 1.0,
        strokeWeight: 2,
        zIndex: 3
    });

    line.shipType = allShips[mmsi].class;

    addToMap(line);
   	historyDrawings[mmsi].push(line);
}



////////////////////////////////// Fetch last points in bounds /////////////////////////
function fetchData(bounds) {
    $.ajax({

        url: '/api/points/last',
        type: 'POST',
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(bounds),
        success: function (response) {

            // Draw the current ships
            writeDataToMap(response);

        },
        error: function () {
            console.log('Failed!');
        },
    });
}

function writeDataToMap(ships) {
    var chunkSize = 10;
    var slices = [];

    for (var i = 0; i < ships.length / chunkSize; i++) {

        slices.push(ships.slice(i * chunkSize, i * chunkSize + chunkSize));
    }

    chunkTimeout(slices, 0);
}

function chunkTimeout(slices, curr) {
    if (curr == slices.length) {
        return;
    }
    else {
        setTimeout(function () {

            runChunkOfShips(slices[curr]);

            chunkTimeout(slices, curr + 1);
        }, 100);
    }
}

function runChunkOfShips(chunk) {
    for (var i = 0; i < chunk.length; i++) {

        // Add to all ships
        if (!allShips[chunk[i].mmsi]) {
            writeSingleShip(chunk[i]);

            allShips[chunk[i].mmsi] = chunk[i];
            chunk[i].infoView = false;
        }
    }
}


function writeSingleShip(ship) {
    // If the ship is already shown, do nothing :)
    if (ship.mmsi in allShips) {
        return;
    }

    var currentCoordinates = { lat: ship.lat, lng: ship.lon };

    var marker = new google.maps.Marker({
        position: currentCoordinates,
        icon: {
            path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
            rotation: ship.course,
            strokeWeight: 2,
            fillColor: '#00F',
            strokeColor: shipTypeToColor(ship.class),
            scale: 4,
            zIndex: 5
        }
    });

    marker.shipType = ship.class;

    marker.addListener('click', function () {

        if (allShips[ship.mmsi].infoView == false) {

            $.getJSON('/api/entity/' + ship.mmsi, function (info) {

                var content = "<div style='color:black;'><table class='into-table'>";

                content += "<tr><td colspan='2'>"+
                			"<img src='http://www.myshiptracking.com/requests/getpic.php?mmsi="+ship.mmsi+"'>"
                		"</td></tr>";

                var keys = Object.keys(info);
                
                keys.forEach(function (key) {
                    content += "<tr>";
                    content += "<td><strong>" + key + ":&nbsp;&nbsp;</strong></td>";
                    content += "<td>" + info[key];
                    if (key == 'flag') {
                        var cc = /\[(\w{2})\]/.exec(info[key])[1] || '';
                        content += "<img src='/client/res/flags/" + cc.toLowerCase() + ".png' width='18' height='12'>"
                    }
                    content += "</td>";
                    content += "</tr>";
                });

                content += "</table></div>";

                var infowindow = new google.maps.InfoWindow({
                    content: content
                });

                infowindow.open(map, marker);
                allShips[ship.mmsi].infoView = true;

                google.maps.event.addListener(infowindow, 'closeclick', function () {

                    // Delete history
                    setTimeout(function () {
                        for (var i = 0; i < historyDrawings[ship.mmsi].length; i++) {
                            var item = historyDrawings[ship.mmsi][i];
                            removeFromMap(item);
                            historyDrawings[ship.mmsi][i] = null;
                        }

                        historyDrawings[ship.mmsi] = [];

                    }, 0);

                    allShips[ship.mmsi].infoView = false;
                });
            });

        }


        // If history isn't shown, show it
        if (!historyDrawings[ship.mmsi] || historyDrawings[ship.mmsi].length == 0) {

            fetchPointsOfShip(ship.mmsi);
        }
    });

    addToMap(marker);
}

var featuresInMap = [];

function addToMap(f) {
    featuresInMap.push(f);
    f.setMap(map);
}

function removeFromMap(f) {
    var idx = featuresInMap.indexOf(f);
    if (idx > -1){
        featuresInMap.splice(idx, 1);
        f.setMap(null);
    }
}

function paintAllShips() {
    shuldPaintAllInSameColor = false;

    featuresInMap.forEach(function (f) {
        var icon = f.icon;
        icon.strokeColor = shipTypeToColor(f.shipType);
        f.setIcon(icon);
    });
}

function shipTypeToColor(type) {
    if (shuldPaintAllInSameColor) {
        return '#9D00FF';
    } else if (type == "Tanker")
        return "#f4f142";
    else if (type == "Cargo")
        return "#686726";
    else if (type == "Passenger")
        return "#28EB21";
    else if (type == "Tow")
        return "#21C6EB";
    else if (type == "Base")
        return "#EB21AB";
    else if (type == "Container")
        return "#75536B";
    else if (type == "Fishing")
        return "#A0B038";
    else if (type == "Speed")
        return "#F53A1D";
    else if (type == "Army")
        return "#E61919";
    else if (type == "Supply")
        return "#E68D19";
    else
        return "#EDEDED";
}