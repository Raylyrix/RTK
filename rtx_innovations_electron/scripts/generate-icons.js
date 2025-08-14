const fs = require('fs');
const path = require('path');
const iconGen = require('icon-gen');
const sharp = require('sharp');

(async () => {
	try {
		const assetsDir = path.join(__dirname, '../assets');
		const iconsDir = path.join(assetsDir, 'icons');
		if (!fs.existsSync(iconsDir)) fs.mkdirSync(iconsDir, { recursive: true });
		const src = path.join(assetsDir, 'logo.png');
		if (!fs.existsSync(src)) {
			console.log('No assets/logo.png found; skipping icon generation');
			process.exit(0);
		}
		// Validate PNG and normalize to 1024x1024
		const tmpPng = path.join(iconsDir, 'icon-1024.png');
		await sharp(src).resize(1024, 1024, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toFile(tmpPng);

		await iconGen(tmpPng, iconsDir, {
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