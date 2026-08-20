import { readFileSync, writeFileSync } from 'fs';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { USDZExporter } from 'three/examples/jsm/exporters/USDZExporter.js';

const src = process.argv[2];
const dst = process.argv[3];
const buf = readFileSync(src);
const loader = new GLTFLoader();

loader.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength), '', async (gltf) => {
  const scene = new THREE.Scene();
  scene.add(gltf.scene);
  const exporter = new USDZExporter();
  const data = await exporter.parseAsync(gltf.scene);
  writeFileSync(dst, Buffer.from(data));
  console.log('wrote', dst, data.byteLength);
}, (err) => {
  console.error(err);
  process.exit(1);
});
