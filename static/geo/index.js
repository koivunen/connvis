var map = L.map('map', {
    minZoom: 2.2,
    maxZoom: 6,
}),
    realtime = L.realtime({
        url: '/geo.json',
        crossOrigin: true,
        type: 'json'
    }, {
        interval: 1 * 1000,
        removeMissing: true
    }).addTo(map);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var first=true;
realtime.on('update', function () {
    if (first) {
        first=false;

        map.setView([0, 0], 0);
    };
});