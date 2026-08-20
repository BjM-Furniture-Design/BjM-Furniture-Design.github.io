import { readFileSync, writeFileSync } from 'fs';
import { createRequire } from 'module';
import { Blob } from 'buffer';

const require = createRequire(import.meta.url);
const { Image, createCanvas } = require('canvas');

globalThis.self = globalThis;
globalThis.window = globalThis;
globalThis.document = {
  createElementNS: (_ns, tag) => {
    if (tag === 'img') return new Image();
    if (tag === 'canvas') {
      const c = createCanvas(1, 1);
      return c;
    }
    return {};
  },
  createElement: (tag) => {
    if (tag === 'img') return new Image();
    if (tag === 'canvas') return createCanvas(1, 1);
    return {};
  },
};
globalThis.Image = Image;
globalThis.Blob = Blob;
globalThis.HTMLImageElement = Image;
globalThis.HTMLCanvasElement = Object.getPrototypeOf(createCanvas(1, 1)).constructor;

const THREE = await import('three');
const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
const { USDZExporter } = await import('three/examples/jsm/exporters/USDZExporter.js');

const src = process.argv[2];
const dst = process.argv[3];
const buf = readFileSync(src);
const loader = new GLTFLoader();

await new Promise((resolve, reject) => {
  loader.parse(
    buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength),
    '',
    async (gltf) => {
      const exporter = new USDZExporter();
      const data = await exporter.parseAsync(gltf.scene);
      writeFileSync(dst, Buffer.from(data));
      console.log('wrote', dst, data.byteLength);
      resolve();
    },
    reject
  );
});
