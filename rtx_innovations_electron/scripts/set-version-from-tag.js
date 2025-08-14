const fs = require('fs');
const path = require('path');

function main() {
  const cwd = process.cwd();
  const pkgPath = path.join(cwd, 'package.json');
  const tag = process.env.GITHUB_REF_NAME || process.env.TAG || '';
  if (!tag) {
    console.error('No tag detected in GITHUB_REF_NAME/TAG');
    process.exit(0);
  }
  const ver = tag.replace(/^v/i, '');
  if (!/^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$/.test(ver)) {
    console.error('Tag does not look like semver:', tag);
    process.exit(1);
  }
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  pkg.version = ver;
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));
  console.log('package.json version set to', ver);
}

main();


