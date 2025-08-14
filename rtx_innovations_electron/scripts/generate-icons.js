const fs = require('fs');
const path = require('path');
const iconGen = require('icon-gen');

function resolveSourcePng() {
	const candidates = [
		path.join(__dirname, '../assets/icons/logo.png'),
		path.join(__dirname, '../assets/logo.png')
	];
	for (const p of candidates) { if (fs.existsSync(p)) return p; }
	return null;
}

(async () => {
	try {
		const assetsDir = path.join(__dirname, '../assets');
		const iconsDir = path.join(assetsDir, 'icons');
		if (!fs.existsSync(iconsDir)) fs.mkdirSync(iconsDir, { recursive: true });
		const src = resolveSourcePng();
		if (!src) {
			console.log('No logo.png found at assets/icons/logo.png or assets/logo.png; skipping icon generation');
			process.exit(0);
		}

		// Try to normalize with sharp if available; otherwise fallback to raw PNG
		let tmpPng = path.join(iconsDir, 'icon-1024.png');
		let usedSharp = false;
		try {
			const sharp = require('sharp');
			await sharp(src).resize(1024, 1024, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toFile(tmpPng);
			usedSharp = true;
		} catch (e) {
			try { fs.copyFileSync(src, tmpPng); } catch (_) { tmpPng = src; }
			console.log('sharp not available or failed; using source PNG directly');
		}

		await iconGen(tmpPng, iconsDir, {
			report: true,
			icns: { name: 'icon' },
			ico: { name: 'icon' },
			favicon: { pngSizes: [256], name: 'icon' }
		});
		console.log('Icons generated at', iconsDir, 'sharpUsed=', usedSharp);
	} catch (e) {
		console.error('Icon generation failed:', e.message);
		process.exit(0);
	}
})(); 