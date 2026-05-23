import {
  Vec3, Mat4, vec3, mat4, mat4Identity, mat4Multiply,
  mat4Perspective, mat4LookAt, mat4Translate, mat4RotateY, mat4Scale,
} from './math';
import { loadGlb } from './glb-loader';
import { BG_VERT, BG_FRAG, BLIT_VERT, CAR_VERT, CAR_FRAG } from './shaders';

const DEG = Math.PI / 180;

interface GpuPrimitive {
  posBuf: WebGLBuffer;
  normBuf: WebGLBuffer | null;
  uvBuf: WebGLBuffer | null;
  idxBuf: WebGLBuffer | null;
  idxCount: number;
  idxType: number;
  vertCount: number;
  texture: WebGLTexture | null;
  nodeTransform: Mat4;
}

function compileShader(gl: WebGLRenderingContext, type: number, src: string): WebGLShader {
  const s = gl.createShader(type)!;
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(s);
    gl.deleteShader(s);
    throw new Error('Shader compile: ' + log);
  }
  return s;
}

function linkProgram(gl: WebGLRenderingContext, vs: string, fs: string): WebGLProgram {
  const prog = gl.createProgram()!;
  gl.attachShader(prog, compileShader(gl, gl.VERTEX_SHADER, vs));
  gl.attachShader(prog, compileShader(gl, gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    const log = gl.getProgramInfoLog(prog);
    gl.deleteProgram(prog);
    throw new Error('Program link: ' + log);
  }
  return prog;
}

function loadImage(src: string | Blob): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('Failed to load image'));
    if (src instanceof Blob) img.src = URL.createObjectURL(src);
    else img.src = src;
  });
}

function uploadTexture(gl: WebGLRenderingContext, img: HTMLImageElement): WebGLTexture {
  const tex = gl.createTexture()!;
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  return tex;
}

function makeWhiteTexture(gl: WebGLRenderingContext): WebGLTexture {
  const tex = gl.createTexture()!;
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([255, 255, 255, 255]));
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  return tex;
}

export class Renderer {
  private gl: WebGLRenderingContext;
  private bgProg!: WebGLProgram;
  private carProg!: WebGLProgram;
  private blitProg!: WebGLProgram;
  private bgTex!: WebGLTexture;
  private quadBuf!: WebGLBuffer;
  private gpuPrims: GpuPrimitive[] = [];
  private defaultTex!: WebGLTexture;
  private modelCenter: Vec3 = vec3(0, 0, 0);

  private fbo!: WebGLFramebuffer;
  private fboColorTex!: WebGLTexture;
  private fboDepthRb!: WebGLRenderbuffer;
  private ssScale = 2;

  eyeX = 0; eyeY = 10; eyeZ = 60;
  lookX = 0; lookZ = 0;
  fov = 15;

  carX = 0;
  carZ = 0;
  carRotation = 0;
  carScale = 0.75;

  private lightDir = vec3(0.3, 0.8, 0.5);

  constructor(private canvas: HTMLCanvasElement) {
    const gl = canvas.getContext('webgl', {
      alpha: false,
      antialias: true,
      depth: true,
      premultipliedAlpha: false,
      preserveDrawingBuffer: false,
    });
    if (!gl) throw new Error('WebGL not supported');
    this.gl = gl;
    gl.getExtension('OES_element_index_uint');
  }

  async load(snapshotUrl: string, modelUrl: string, fallbackTextureUrl: string): Promise<{ width: number; height: number }> {
    const gl = this.gl;

    this.bgProg = linkProgram(gl, BG_VERT, BG_FRAG);
    this.carProg = linkProgram(gl, CAR_VERT, CAR_FRAG);

    this.quadBuf = gl.createBuffer()!;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);

    this.defaultTex = makeWhiteTexture(gl);

    const [bgImg, glbBuf] = await Promise.all([
      loadImage(snapshotUrl),
      fetch(modelUrl).then(r => r.arrayBuffer()),
    ]);

    const rw = bgImg.naturalWidth;
    const rh = bgImg.naturalHeight;
    this.canvas.width = rw;
    this.canvas.height = rh;

    this.bgTex = uploadTexture(gl, bgImg);

    const model = loadGlb(glbBuf);

    const bmin = model.boundingBox.min;
    const bmax = model.boundingBox.max;
    this.modelCenter = vec3(
      -(bmin[0] + bmax[0]) / 2,
      -bmin[1],
      -(bmin[2] + bmax[2]) / 2,
    );

    const textures: (WebGLTexture | null)[] = [];
    for (const embeddedImg of model.images) {
      const blob = new Blob([embeddedImg.data.buffer as ArrayBuffer], { type: embeddedImg.mimeType });
      textures.push(uploadTexture(gl, await loadImage(blob)));
    }
    let fallbackTex: WebGLTexture | null = null;
    try {
      fallbackTex = uploadTexture(gl, await loadImage(fallbackTextureUrl));
    } catch {}

    for (const prim of model.primitives) {
      const posBuf = gl.createBuffer()!;
      gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
      gl.bufferData(gl.ARRAY_BUFFER, prim.positions, gl.STATIC_DRAW);

      let normBuf: WebGLBuffer | null = null;
      if (prim.normals) {
        normBuf = gl.createBuffer()!;
        gl.bindBuffer(gl.ARRAY_BUFFER, normBuf);
        gl.bufferData(gl.ARRAY_BUFFER, prim.normals, gl.STATIC_DRAW);
      }

      let uvBuf: WebGLBuffer | null = null;
      if (prim.texcoords) {
        uvBuf = gl.createBuffer()!;
        gl.bindBuffer(gl.ARRAY_BUFFER, uvBuf);
        gl.bufferData(gl.ARRAY_BUFFER, prim.texcoords, gl.STATIC_DRAW);
      }

      let idxBuf: WebGLBuffer | null = null;
      let idxCount = 0;
      let idxType: number = gl.UNSIGNED_SHORT;
      if (prim.indices) {
        idxBuf = gl.createBuffer()!;
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, idxBuf);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, prim.indices, gl.STATIC_DRAW);
        idxCount = prim.indices.length;
        idxType = prim.indices instanceof Uint32Array ? gl.UNSIGNED_INT : gl.UNSIGNED_SHORT;
      }

      let tex: WebGLTexture | null = null;
      if (prim.materialIndex >= 0 && prim.materialIndex < model.materialTextureIndex.length) {
        const imgIdx = model.materialTextureIndex[prim.materialIndex];
        if (imgIdx >= 0 && imgIdx < textures.length && textures[imgIdx]) {
          tex = textures[imgIdx];
        }
      }
      if (!tex) tex = fallbackTex;

      this.gpuPrims.push({
        posBuf, normBuf, uvBuf, idxBuf, idxCount, idxType,
        vertCount: prim.positions.length / 3,
        texture: tex,
        nodeTransform: prim.nodeTransform,
      });
    }

    const ld = this.lightDir;
    const len = Math.sqrt(ld[0] * ld[0] + ld[1] * ld[1] + ld[2] * ld[2]);
    ld[0] /= len; ld[1] /= len; ld[2] /= len;

    gl.disable(gl.CULL_FACE);

    const ssW = rw * this.ssScale;
    const ssH = rh * this.ssScale;

    this.fboColorTex = gl.createTexture()!;
    gl.bindTexture(gl.TEXTURE_2D, this.fboColorTex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, ssW, ssH, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

    this.fboDepthRb = gl.createRenderbuffer()!;
    gl.bindRenderbuffer(gl.RENDERBUFFER, this.fboDepthRb);
    gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_COMPONENT16, ssW, ssH);

    this.fbo = gl.createFramebuffer()!;
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.fboColorTex, 0);
    gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.RENDERBUFFER, this.fboDepthRb);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);

    this.blitProg = linkProgram(gl, BLIT_VERT, BG_FRAG);

    return { width: rw, height: rh };
  }

  render() {
    const gl = this.gl;
    const c = gl.canvas as HTMLCanvasElement;
    const nw = c.width, nh = c.height;

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, nw, nh);
    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    gl.disable(gl.DEPTH_TEST);
    gl.depthMask(false);
    gl.useProgram(this.bgProg);

    const bgPosLoc = gl.getAttribLocation(this.bgProg, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuf);
    gl.enableVertexAttribArray(bgPosLoc);
    gl.vertexAttribPointer(bgPosLoc, 2, gl.FLOAT, false, 0, 0);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.bgTex);
    gl.uniform1i(gl.getUniformLocation(this.bgProg, 'u_tex'), 0);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    gl.disableVertexAttribArray(bgPosLoc);

    if (this.gpuPrims.length === 0) return;

    const ssW = nw * this.ssScale;
    const ssH = nh * this.ssScale;
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.viewport(0, 0, ssW, ssH);
    // depthMask must be re-enabled BEFORE clear, or depth buffer is skipped
    gl.depthMask(true);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    gl.enable(gl.DEPTH_TEST);
    gl.useProgram(this.carProg);

    const aspect = nw / nh;
    const proj = mat4Perspective(mat4(), this.fov * DEG, aspect, 0.1, 500);
    const view = mat4LookAt(mat4(),
      vec3(this.eyeX, this.eyeY, this.eyeZ),
      vec3(this.lookX, 0, this.lookZ),
      vec3(0, 1, 0));

    const model = mat4Identity(mat4());
    mat4Translate(model, model, vec3(this.carX, 0, this.carZ));
    mat4RotateY(model, model, this.carRotation * DEG);
    mat4Scale(model, model, vec3(this.carScale, this.carScale, this.carScale));
    mat4Translate(model, model, this.modelCenter);

    const uMvp = gl.getUniformLocation(this.carProg, 'u_mvp');
    const uModel = gl.getUniformLocation(this.carProg, 'u_model');
    const uTex = gl.getUniformLocation(this.carProg, 'u_tex');
    const uLight = gl.getUniformLocation(this.carProg, 'u_lightDir');

    const aPosLoc = gl.getAttribLocation(this.carProg, 'a_position');
    const aNormLoc = gl.getAttribLocation(this.carProg, 'a_normal');
    const aUvLoc = gl.getAttribLocation(this.carProg, 'a_texcoord');

    gl.uniform3fv(uLight, this.lightDir);
    gl.uniform1i(uTex, 0);

    const vp = mat4Multiply(mat4(), proj, view);

    for (const prim of this.gpuPrims) {
      const modelNode = mat4Multiply(mat4(), model, prim.nodeTransform);
      const mvp = mat4Multiply(mat4(), vp, modelNode);
      gl.uniformMatrix4fv(uMvp, false, mvp);
      gl.uniformMatrix4fv(uModel, false, modelNode);

      gl.bindBuffer(gl.ARRAY_BUFFER, prim.posBuf);
      gl.enableVertexAttribArray(aPosLoc);
      gl.vertexAttribPointer(aPosLoc, 3, gl.FLOAT, false, 0, 0);

      if (prim.normBuf && aNormLoc >= 0) {
        gl.bindBuffer(gl.ARRAY_BUFFER, prim.normBuf);
        gl.enableVertexAttribArray(aNormLoc);
        gl.vertexAttribPointer(aNormLoc, 3, gl.FLOAT, false, 0, 0);
      } else if (aNormLoc >= 0) {
        gl.disableVertexAttribArray(aNormLoc);
        gl.vertexAttrib3f(aNormLoc, 0, 1, 0);
      }

      if (prim.uvBuf && aUvLoc >= 0) {
        gl.bindBuffer(gl.ARRAY_BUFFER, prim.uvBuf);
        gl.enableVertexAttribArray(aUvLoc);
        gl.vertexAttribPointer(aUvLoc, 2, gl.FLOAT, false, 0, 0);
      } else if (aUvLoc >= 0) {
        gl.disableVertexAttribArray(aUvLoc);
        gl.vertexAttrib2f(aUvLoc, 0, 0);
      }

      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, prim.texture || this.defaultTex);

      if (prim.idxBuf) {
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, prim.idxBuf);
        gl.drawElements(gl.TRIANGLES, prim.idxCount, prim.idxType, 0);
      } else {
        gl.drawArrays(gl.TRIANGLES, 0, prim.vertCount);
      }
    }

    if (aPosLoc >= 0) gl.disableVertexAttribArray(aPosLoc);
    if (aNormLoc >= 0) gl.disableVertexAttribArray(aNormLoc);
    if (aUvLoc >= 0) gl.disableVertexAttribArray(aUvLoc);

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, nw, nh);
    gl.disable(gl.DEPTH_TEST);
    gl.depthMask(false);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    gl.useProgram(this.blitProg);
    const blitPosLoc = gl.getAttribLocation(this.blitProg, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuf);
    gl.enableVertexAttribArray(blitPosLoc);
    gl.vertexAttribPointer(blitPosLoc, 2, gl.FLOAT, false, 0, 0);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.fboColorTex);
    gl.uniform1i(gl.getUniformLocation(this.blitProg, 'u_tex'), 0);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    gl.disableVertexAttribArray(blitPosLoc);

    gl.disable(gl.BLEND);
  }
}
