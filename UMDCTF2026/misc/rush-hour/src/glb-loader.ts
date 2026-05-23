import { Mat4, mat4, mat4Identity, mat4Multiply, mat4Translate, mat4Scale, quatToMat4, vec3 } from './math';

export interface GlbPrimitive {
  positions: Float32Array;
  normals: Float32Array | null;
  texcoords: Float32Array | null;
  indices: Uint16Array | Uint32Array | null;
  materialIndex: number;
  nodeTransform: Mat4;
}

export interface GlbImage {
  data: Uint8Array;
  mimeType: string;
}

export interface GlbModel {
  primitives: GlbPrimitive[];
  images: GlbImage[];
  materialTextureIndex: number[];
  boundingBox: { min: Float32Array; max: Float32Array };
}

const TYPE_COUNTS: Record<string, number> = {
  SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT2: 4, MAT3: 9, MAT4: 16,
};

const COMP_BYTES: Record<number, number> = {
  5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4,
};

function readAccessor(gltf: any, idx: number, bin: ArrayBuffer): Float32Array | Uint16Array | Uint32Array {
  const acc = gltf.accessors[idx];
  const bv = gltf.bufferViews[acc.bufferView];
  const compBytes = COMP_BYTES[acc.componentType];
  const numComp = TYPE_COUNTS[acc.type];
  const elemBytes = compBytes * numComp;
  const bvOffset = bv.byteOffset || 0;
  const accOffset = acc.byteOffset || 0;
  const totalOffset = bvOffset + accOffset;
  const stride = bv.byteStride || 0;

  let Ctor: typeof Float32Array | typeof Uint16Array | typeof Uint32Array;
  if (acc.componentType === 5126) Ctor = Float32Array;
  else if (acc.componentType === 5123 || acc.componentType === 5122) Ctor = Uint16Array;
  else if (acc.componentType === 5125) Ctor = Uint32Array;
  else Ctor = Float32Array;

  const count = acc.count;

  if ((stride === 0 || stride === elemBytes) && totalOffset % compBytes === 0) {
    return new Ctor(bin, totalOffset, count * numComp);
  }

  const result = new Ctor(count * numComp);
  const dv = new DataView(bin);
  const actualStride = stride || elemBytes;
  for (let i = 0; i < count; i++) {
    const base = totalOffset + i * actualStride;
    for (let j = 0; j < numComp; j++) {
      const off = base + j * compBytes;
      if (acc.componentType === 5126) (result as Float32Array)[i * numComp + j] = dv.getFloat32(off, true);
      else if (acc.componentType === 5123) (result as Uint16Array)[i * numComp + j] = dv.getUint16(off, true);
      else if (acc.componentType === 5125) (result as Uint32Array)[i * numComp + j] = dv.getUint32(off, true);
    }
  }
  return result;
}

function getNodeTransform(node: any): Mat4 {
  const out = mat4();
  if (node.matrix) {
    for (let i = 0; i < 16; i++) out[i] = node.matrix[i];
    return out;
  }
  mat4Identity(out);
  if (node.translation) {
    mat4Translate(out, out, vec3(node.translation[0], node.translation[1], node.translation[2]));
  }
  if (node.rotation) {
    const rot = mat4();
    quatToMat4(rot, node.rotation);
    mat4Multiply(out, out, rot);
  }
  if (node.scale) {
    mat4Scale(out, out, vec3(node.scale[0], node.scale[1], node.scale[2]));
  }
  return out;
}

export function loadGlb(buffer: ArrayBuffer): GlbModel {
  const header = new DataView(buffer, 0, 12);
  const magic = header.getUint32(0, true);
  if (magic !== 0x46546C67) throw new Error('Not a GLB file');

  let jsonStr = '';
  let binChunk: ArrayBuffer = new ArrayBuffer(0);
  let offset = 12;
  while (offset < buffer.byteLength) {
    const chunkLen = new DataView(buffer, offset, 4).getUint32(0, true);
    const chunkType = new DataView(buffer, offset + 4, 4).getUint32(0, true);
    const chunkData = buffer.slice(offset + 8, offset + 8 + chunkLen);
    if (chunkType === 0x4E4F534A) {
      jsonStr = new TextDecoder().decode(chunkData);
    } else if (chunkType === 0x004E4942) {
      binChunk = chunkData;
    }
    offset += 8 + chunkLen;
  }

  const gltf = JSON.parse(jsonStr);

  const images: GlbImage[] = [];
  if (gltf.images) {
    for (const img of gltf.images) {
      if (img.bufferView !== undefined) {
        const bv = gltf.bufferViews[img.bufferView];
        const bvOff = bv.byteOffset || 0;
        const data = new Uint8Array(binChunk, bvOff, bv.byteLength);
        images.push({ data: new Uint8Array(data), mimeType: img.mimeType || 'image/jpeg' });
      }
    }
  }

  const materialTextureIndex: number[] = [];
  if (gltf.materials) {
    for (const mat of gltf.materials) {
      const pbr = mat.pbrMetallicRoughness;
      if (pbr?.baseColorTexture !== undefined) {
        const texIdx = pbr.baseColorTexture.index;
        const tex = gltf.textures[texIdx];
        materialTextureIndex.push(tex.source !== undefined ? tex.source : -1);
      } else {
        materialTextureIndex.push(-1);
      }
    }
  }

  const primitives: GlbPrimitive[] = [];
  const bboxMin = new Float32Array([Infinity, Infinity, Infinity]);
  const bboxMax = new Float32Array([-Infinity, -Infinity, -Infinity]);

  function traverse(nodeIdx: number, parentTransform: Mat4) {
    const node = gltf.nodes[nodeIdx];
    const local = getNodeTransform(node);
    const world = mat4();
    mat4Multiply(world, parentTransform, local);

    if (node.mesh !== undefined) {
      const mesh = gltf.meshes[node.mesh];
      for (const prim of mesh.primitives) {
        const attrs = prim.attributes;
        const positions = readAccessor(gltf, attrs.POSITION, binChunk) as Float32Array;
        const normals = attrs.NORMAL !== undefined ? readAccessor(gltf, attrs.NORMAL, binChunk) as Float32Array : null;
        const texcoords = attrs.TEXCOORD_0 !== undefined ? readAccessor(gltf, attrs.TEXCOORD_0, binChunk) as Float32Array : null;
        const indices = prim.indices !== undefined ? readAccessor(gltf, prim.indices, binChunk) as Uint16Array | Uint32Array : null;

        for (let i = 0; i < positions.length; i += 3) {
          for (let j = 0; j < 3; j++) {
            if (positions[i + j] < bboxMin[j]) bboxMin[j] = positions[i + j];
            if (positions[i + j] > bboxMax[j]) bboxMax[j] = positions[i + j];
          }
        }

        primitives.push({
          positions,
          normals,
          texcoords,
          indices,
          materialIndex: prim.material !== undefined ? prim.material : -1,
          nodeTransform: world,
        });
      }
    }

    if (node.children) {
      for (const child of node.children) {
        traverse(child, world);
      }
    }
  }

  const identity = mat4();
  mat4Identity(identity);
  if (gltf.scenes && gltf.scenes.length > 0) {
    const sceneIdx = gltf.scene !== undefined ? gltf.scene : 0;
    const scene = gltf.scenes[sceneIdx];
    if (scene.nodes) {
      for (const nodeIdx of scene.nodes) {
        traverse(nodeIdx, identity);
      }
    }
  } else if (gltf.nodes) {
    for (let i = 0; i < gltf.nodes.length; i++) {
      traverse(i, identity);
    }
  }

  return { primitives, images, materialTextureIndex, boundingBox: { min: bboxMin, max: bboxMax } };
}
