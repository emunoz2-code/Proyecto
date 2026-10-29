// Renderizado opcional de los SVG. Pasar la ruta de un módulo sharp instalado.
const fs = require('fs');
const path = require('path');
const sharp = require(process.argv[2] || 'sharp');
async function main() {
  const dir = path.resolve(__dirname, '..', 'diagrams');
  for (const name of ['arquitectura', 'conexiones']) {
    await sharp(fs.readFileSync(path.join(dir, name + '.svg')))
      .png().toFile(path.join(dir, name + '.png'));
  }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
