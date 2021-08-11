
var map = L.map('map', {
	minZoom: 2.2,
	maxZoom: 8,
});
var only_circles = false;

var realtime = L.realtime({
	url: '/geo.json',
	crossOrigin: true,
	type: 'json'
}, {
	interval: 1 * 1000,
	removeMissing: true,
	pointToLayer: function (feature, latlng) {

		var data = feature["properties"];
		var last_activity = data["last_activity"];
		var last_activity_msec = data["last_activity_msec"];

		var m = L.circleMarker(latlng, {
			radius: 50
		});

		m.feature = feature;

		var targetnames = data["targetnames"];
		var targetnames_ads = data["targetnames_ads"];
		var targets = data["targets"];
		var targets_ads = data["targets_ads"];
		var asns = data["asns"];

		var text = data["country_name"];
		text += "<hr>";
		text += data["originators"].map(x => x.replace("\n", " ")).join("<br>");

		text += "<hr>";
		text += targetnames.join("<br>");
		if (targetnames.length > 0) { text += "<br>"; };

		text += targetnames_ads.map(x => '<a class="adlabel" target="_blank" href="https://google.com/search?q=' + encodeURIComponent(x) + '">' + x + '</a>').join("<br>");
		if (targetnames.length > 0 || targetnames_ads.length > 0) { text += "<hr>"; }

		text += asns.map(x => '<a class="asnlabel" target="_blank" href="https://google.com/search?q=' + encodeURIComponent(x) + '">' + x + '</a>').join("<br>");
		m.bindTooltip(text, {
			interactive: !only_circles ,
			permanent: !only_circles ,
			direction: 'center',
			className: 'locinfolabel',
		});

		var text2 = "";
		text2 += targets.map(x => '<a class="targetlabel" target="_blank" href="https://www.ip2location.com/' + encodeURIComponent(x) + '">' + x + '</a>').join("<br>");
		text += "<hr>";
		text2 += targets_ads.map(x => '<a class="adlabel" target="_blank" href="https://www.ip2location.com/' + encodeURIComponent(x) + '">' + x + '</a>').join("<br>");
		var pop = m.bindPopup(text2, { closeOnClick: true, autoClose: true });
		//setTimeout(1, function () { pop.openPopup(); });
		return m;
	}
});
realtime.addTo(map);

function UpdateHotness() {
	map.eachLayer(function (marker) {
		if (!marker._radius) return;
		if (!marker.feature.properties.last_activity) return;
		var age = new Date() / 1000 - marker.feature.properties.last_activity;
		var hotness = (15 - age) / 15;
		hotness = Math.min(1, Math.max(hotness, 0));
		var e = marker.getTooltip().getElement();
		marker.setRadius(10 + hotness * 30);
		if (!e) return;
		if (!e.style) return;
		e.style.borderColor = "rgb(" + Math.round(hotness * 255) + ",0,0)";
	});
}

setInterval(UpdateHotness, 100);


L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var first = true;
realtime.on('update', function () {
	if (first) {
		first = false;
		map.setView([0, 0], 0);
	};

});

var tipcycler_ids={};
function tipcycler_cb() {
	var done=false;
	map.eachLayer(function (marker) {
		
		if (!marker._radius) return;
		if (!marker.feature.properties.last_activity) return;
		var tip = marker.getTooltip();
		
		if (marker.visited_tip) {
			map.closeTooltip(tip);
			return;
		};

		done=true;
		marker.visited_tip=true;
		map.openTooltip(tip);
	});

	if (done) return;

	map.eachLayer(function (marker) {
		if (!marker._radius) return;
		if (!marker.feature.properties.last_activity) return;
		var tip = marker.getTooltip();
		marker.visited_tip=false;
	});
	tipcycler_cb();
}
var tipcycler;

var btn3 = L.easyButton({
	position: 'topleft',
	states: [{
		stateName: 'on',
		icon: '<span>ON</span>',
		title: 'state',
		onClick: function (control) {
			control.state('off')
			tipcycler=setInterval(tipcycler_cb,1000);
		},
	},
	{
		stateName: 'off',
		icon: '<span>OFF</span>',
		title: 'state',
		onClick: function (control) {
			control.state('on')
			clearInterval(tipcycler);
		},
	}]
});
btn3.addTo(map);

map.on('load', function () {

	var command = L.control({ position: 'topleft' });

	command.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'command');

		div.innerHTML = '<form><input id="command" name="command" type="checkbox"/><label for="command">Pause</label></form>';
		return div;
	};

	command.addTo(map);


	// add the event handler
	function handleCommand() {
		var paused = this.checked;
		if (paused) {
			realtime.stop();
		} else {
			realtime.start();
		}
	}

	document.getElementById("command").addEventListener("click", handleCommand, false);
});

map.on('load', function () {

	var command = L.control({ position: 'topleft' });

	command.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'command');

		div.innerHTML = '<form><input id="command2" name="command2" type="checkbox"/><label for="command2">Hide tooltips</label></form>';
		return div;
	};

	command.addTo(map);


	document.getElementById("command2").addEventListener("click", function () {
		only_circles = this.checked;
		map.eachLayer(function (marker) {
			if (!marker._radius) return;
			if (!marker.feature.properties.last_activity_msec) return;
			if (marker.getTooltip()) {
				var tooltip = marker.getTooltip();
				marker.unbindTooltip().bindTooltip(tooltip, {
					interactive: !only_circles,
					permanent: !only_circles ,
					direction: 'center',
					className: 'locinfolabel',
				});
			}
		});

	}, false);
});

