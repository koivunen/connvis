'use strict';

var colorGenerator = d3.scaleOrdinal(d3.schemeCategory10);
var layout = d3.sankey()
	.extent([[100, 15], [1280 - 50 - 150, 1024 - 30]]);
var diag = d3.sankeyDiagram()
	.nodeTitle(function (d) { return d.title || d.id; })
	.linkColor(function (d) { return d.color || colorGenerator(d.id); })
	.linkLabel(function (d) { return Math.round(d.last_act) || ""; })
	.linkTitle(function (d) { return d.actualtargets.join('\n'); })
	.on("selectNode",function(n){
		console.log("selectNode",n);
		if (n&&n.id)
		window.open("https://www.google.com/search?q="+n.id.replace("*",""));
	});
function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

async function updateLoop() {
	var svg = d3.select('#sankey svg');

	const interpolate = d3.interpolateRgb("steelblue", "brown");
	while (1) {
		while (document.getElementById("pausebtn").checked) {
			await sleep(333);
		};

		try {
			let response = await fetch('/sankey.json');
			var data = await response.json();
			var links = data.links;
			for (const [key, link] of Object.entries(links)) {
				const max_age=10;
				var last_act=link.last_act;
				const ageness=Math.min(Math.max(max_age/last_act, 0), 1);
				
				link["color"]=interpolate(ageness);
			}
			d3.select('#error').text('');
			d3.select('#containing').text(data.containing=="purged"?"Vain suosituimmat laitteiden yhteiset kohteet":(data.containing=="all"?"Kaikkien laitteiden kaikki kohteet":"Laitteiden yhteiset kohteet"));
			d3.select('#link_count').text(data.link_count);
			d3.select('#link_count_visible').text(data.links.length);
			if (data.links.length==data.link_count) {
				document.getElementById("link_count_visible_wrap").style.display = "none";
			} else {
				document.getElementById("link_count_visible_wrap").style.display = "inline";
			}
		} catch (e) {
			d3.select('#error').text("VIRHE: "+e);
			last_error_data = data;
			await sleep(3000);
			continue;
		}

		//layout.ordering(value.order || null);

		svg.datum(layout.scale(null)(data))
			.transition()
			.duration(600)
			.call(diag)
			
		svg.selectAll('.node')
		.attr('font-weight',"bold")
		.attr('font-style',"serif")
		.attr('fill',function(n){
			return n.ad?"rgb(150,50,0)":"rgb(0,0,0)"
		}).attr('text-decoration',function(n){
			return n.ad?"underline":""
		});

			
		console.log("updating");
		await sleep(997);
	}
}

updateLoop(); //.then(x => document.reload()).catch(x => document.reload())