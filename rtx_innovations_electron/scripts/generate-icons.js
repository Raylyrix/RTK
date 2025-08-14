const fs = require('fs');
const path = require('path');
const iconGen = require('icon-gen');

(async () => {
	try {
		const assetsDir = path.join(__dirname, '../assets');
		const iconsDir = path.join(assetsDir, 'icons');
		if (!fs.existsSync(iconsDir)) fs.mkdirSync(iconsDir, { recursive: true });
		const srcPng = path.join(assetsDir, 'logo.png');
		if (!fs.existsSync(srcPng)) {
			console.log('No assets/logo.png found; skipping icon generation');
			process.exit(0);
		}
		await iconGen(srcPng, iconsDir, {
			report: true,
			icns: { name: 'icon' },
			ico: { name: 'icon' },
			favicon: { pngSizes: [256], name: 'icon' }
		});
		console.log('Icons generated at', iconsDir);
	} catch (e) {
		console.error('Icon generation failed:', e.message);
		process.exit(0);
	}
})(); 