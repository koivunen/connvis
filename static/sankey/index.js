
var colorGenerator = d3.scaleOrdinal(d3.schemeCategory10);
var layout = d3.sankey()
	.extent([[50, 15], [1280 - 50 - 150, 1024 - 30]]);
var diag = d3.sankeyDiagram()
	.nodeTitle(function (d) { return d.title || d.id; })
	.linkColor(function (d) { return d.color || colorGenerator(d.id); })
	.on("selectNode",function(n){
		console.log(n);
	});

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

async function updateLoop() {
	while (1) {

		try {
			let response = await fetch('/sankey.json');
			var data = await response.json();
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
			return;
		}

		//layout.ordering(value.order || null);
		d3.select('#sankey svg')
			.datum(layout.scale(null)(data))
			.transition()
			.duration(600)
			.call(diag);
		console.log("updating");
		await sleep(997);
	}
}

updateLoop(); //.then(x => document.reload()).catch(x => document.reload())