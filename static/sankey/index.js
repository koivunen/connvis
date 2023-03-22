'use strict';
var last_error_data;

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
var loadedData=false; //TODO

var lastDataJson="FAILED";
function download(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}
function DownloadData() {
	download(lastDataJson, 'sankey'+Math.round(new Date().getTime()/1000)+'.json', 'text/plain');
}
function ImportData() {
	var input = document.createElement('input');
	input.type = 'file';

	input.onchange = e => {

		var file = e.target.files[0];

		var reader = new FileReader();
		reader.readAsText(file, 'UTF-8');

		reader.onload = readerEvent => {
			var content = readerEvent.target.result;
			loadedData=JSON.parse(content);
		}

	}

	input.click();
}

async function updateLoop() {
	var svg = d3.select('#sankey svg');

	const interpolate = d3.interpolateRgb("steelblue", "brown");
	while (1) {
		while (document.getElementById("pausebtn").checked) {
			await sleep(333);
		};

		var data = loadedData;
		try {
			if (!data) {
				let response = await fetch('/sankey.json');
				lastDataJson = await response.text();
				data = JSON.parse(lastDataJson);
			}
			var links = data.links;
			for (const [key, link] of Object.entries(links)) {
				const max_age=10;
				var last_act=link.last_act;
				const ageness=Math.min(Math.max(max_age/last_act, 0), 1);
				
				link["color"]=interpolate(ageness);
			}
			d3.select('#error').text('');
			d3.select('#containing').text(data.containing=="purged"?"(VERY LIMITED) Only popular common destinations":(data.containing=="all"?"All":"(LIMITED) Common connections only"));
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
		await sleep(loadedData?4000:997);
	}
}

updateLoop(); //.then(x => document.reload()).catch(x => document.reload())
