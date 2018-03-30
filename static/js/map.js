let map = undefined;
let flightPath = undefined;
let coordinatesArray = [];

function parseCoordinatesMessage(data) {
    let coordinates = data;
    coordinatesArray.push(coordinates);
    if (flightPath === undefined) {
        let flightPath = new google.maps.Polyline({
            path: coordinatesArray,
            geodesic: true,
            strokeColor: '#0000FF',
            strokeOpacity: 0.5,
            strokeWeight: 5
        });
        flightPath.setMap(map);
    } else {
        flightPath.setPath(coordinatesArray);
    }

    map.panTo(coordinates);
}

function initMap() {
    let coordinates = {lat: 47.4734, lng: 19.0598};
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 20,
        center: coordinates,
        mapTypeId: 'hybrid',
    });
    map.setTilt(0);
    google.maps.event.addListener(map, 'click', function (event) {
        placeMarker(event.latLng);
    });
}

function placeMarker(location) {
    if (destination === undefined) {
        updateDestination(location);
        let marker = new google.maps.Marker({
            position: destination,
            map: map,
            draggable: true,
        });
        google.maps.event.addListener(marker, 'dragend', function () {
            updateDestination(marker.getPosition());
        });
        google.maps.event.addListener(marker, 'rightclick', function () {
            marker.setMap(null);
            destination = undefined;
        });
    }
}
