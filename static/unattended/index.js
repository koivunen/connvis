'use strict';

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

async function updateLoop() {

	while (1) {
		//TODO
		await sleep(997);
	}
}

updateLoop(); 