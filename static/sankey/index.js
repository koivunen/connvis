
var tryColor = d3.scaleOrdinal(d3.schemeCategory10);
var tryLayout = d3.sankey()
	.extent([[50, 30], [400, 370]]);
var tryDiagram = d3.sankeyDiagram()
	.nodeTitle(function (d) { return d.title || d.id; })
	.linkColor(function (d) { return d.color || tryColor(d.type); });

function alignLinkTypes(layout, align) {
	return layout
		.sourceId(function (d) {
			return {
				id: typeof d.source === "object" ? d.source.id : d.source,
				port: align ? d.type : null
			};
		})
		.targetId(function (d) {
			return {
				id: typeof d.target === "object" ? d.target.id : d.target,
				port: align ? d.type : null
			};
		});
}

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
  }

async function updateLoop() {
	try {
		
		let response = await fetch('/sankey.json');
		var value = await response.json();
		d3.select('#error').text('');
	} catch (e) {
		d3.select('#error').text(e);
		return;
	}

	tryLayout.ordering(value.order || null);
	alignLinkTypes(tryLayout, value.alignLinkTypes);
	d3.select('#sankey svg')
		.datum(tryLayout.scale(null)(value))
		.transition()
		.duration(600)
		.call(tryDiagram);

	await sleep(997);
}

updateLoop() //.then(x => document.reload()).catch(x => document.reload())