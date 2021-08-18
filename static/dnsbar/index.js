'use strict';

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

const chartDom = document.getElementById('chart');
const myChart = echarts.init(chartDom);

const interpolate = d3.interpolateRgb("steelblue", "brown");

var max_age = 20;


var loadedData=false;
var lastDataJson="FAILED";

async function updateLoop() {
	const domain_devicequeries = [];
	const domains = [];
	const domains_ad = {};
	var lastData;
	function genTooltip(params) {
		if (!(params["dataIndex"] >= 0)) return;

		var bar = lastData.bars[params.dataIndex];
		var str = "";
		str += bar["homeips"].map(x => x.replace("\n", " ")).join("<br>")
		str += "<hr>";

		if (bar["domains"]) {
			str += bar["domains"].map(x => x.replace("\n", " ")).join("<br>")
			str += "<hr>";
		}

		str += "<br>";
		return str;
	}
	var option = {
		xAxis: {
			max: 6,
		},
		yAxis: {
			type: 'category',
			data: domains,
			inverse: true,
			animationDuration: 300,
			animationDurationUpdate: 300,
			axisLabel: {
				textStyle: {
					color: function (value, index) {
						return (value in domains_ad) ? 'red' : 'black';
					},
					fontWeight: "bold",
					fontSize: "15px"

				},
			}
		},
		grid: {
			top:    60,
			bottom: 60,
			left:   '20%',
			right:  '10%',
		  },
		series: [{
			realtimeSort: true,
			name: 'X',
			type: 'bar',
			data: domain_devicequeries,
			label: {
				show: false,
				position: 'right',
				valueAnimation: false
			},
			itemStyle: {
				color: function (params) {
					var bar = lastData.bars[params.dataIndex];
					var age = bar.age;
					const ageness=Math.min(Math.max(max_age/age, 0), 1);
					const col=interpolate(ageness);
					return col;
				}
			}
		}],
		tooltip: {
			formatter: genTooltip
		},
		legend: {
			show: false
		},
		animationDuration: 0,
		animationDurationUpdate: 3000,
		animationEasing: 'linear',
		animationEasingUpdate: 'linear'
	};

	myChart.on('click', params => {
		if (!(params["dataIndex"] >= 0)) return;

		var bar = lastData.bars[params.dataIndex];

		window.open("https://www.google.com/search?q="+bar.name);

	})

	while (1) {
		while (document.getElementById("pausebtn").checked) {
			await sleep(333);
		};

		try {
			var data = loadedData;
			if (!data) {
				let response = await fetch('/dnsbar.json');
				lastDataJson = await response.text();
				lastData = JSON.parse(lastDataJson);
				data = lastData;
			}
			d3.select('#error').text('');
			d3.select('#link_count').text(data.total_domains);
			d3.select('#link_count_visible').text(data.bars.length);
			if (data.bars.length == data.total_domains) {
				document.getElementById("link_count_visible_wrap").style.display = "none";
			} else {
				document.getElementById("link_count_visible_wrap").style.display = "inline";
			}
		} catch (e) {
			d3.select('#error').text("VIRHE: " + e);
			last_error_data = data;
			await sleep(3000);
			continue;
		}

		domain_devicequeries.length = 0
		domains.length = 0

		for (const [domain_id, domain_data] of Object.entries(data.bars)) {
			domains.push(domain_data.name);
			domain_devicequeries.push(domain_data.value);
			if (domain_data.isad) {
				domains_ad[domain_data.name] = true
			}
		}

		myChart.setOption(option);


		console.log("updating");
		await sleep(997);
	}
}

updateLoop(); //.then(x => document.reload()).catch(x => document.reload())



function download(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}
function DownloadData() {
	download(lastDataJson, 'dnsbar-'+Math.round(new Date().getTime()/1000)+'.json', 'text/plain');
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