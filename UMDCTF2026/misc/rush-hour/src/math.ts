export type Vec3 = Float32Array;
export type Mat4 = Float32Array;

export function vec3(x: number, y: number, z: number): Vec3 {
  const out = new Float32Array(3);
  out[0] = x; out[1] = y; out[2] = z;
  return out;
}

export function vec3Sub(out: Vec3, a: Vec3, b: Vec3): Vec3 {
  out[0] = a[0] - b[0]; out[1] = a[1] - b[1]; out[2] = a[2] - b[2];
  return out;
}

export function vec3Scale(out: Vec3, a: Vec3, s: number): Vec3 {
  out[0] = a[0] * s; out[1] = a[1] * s; out[2] = a[2] * s;
  return out;
}

export function vec3Normalize(out: Vec3, a: Vec3): Vec3 {
  const len = Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
  if (len > 1e-8) { out[0] = a[0] / len; out[1] = a[1] / len; out[2] = a[2] / len; }
  else { out[0] = 0; out[1] = 0; out[2] = 0; }
  return out;
}

export function vec3Cross(out: Vec3, a: Vec3, b: Vec3): Vec3 {
  const ax = a[0], ay = a[1], az = a[2];
  const bx = b[0], by = b[1], bz = b[2];
  out[0] = ay * bz - az * by;
  out[1] = az * bx - ax * bz;
  out[2] = ax * by - ay * bx;
  return out;
}

export function vec3Dot(a: Vec3, b: Vec3): number {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

export function mat4(): Mat4 {
  return new Float32Array(16);
}

export function mat4Identity(out: Mat4): Mat4 {
  out.fill(0);
  out[0] = out[5] = out[10] = out[15] = 1;
  return out;
}

export function mat4Multiply(out: Mat4, a: Mat4, b: Mat4): Mat4 {
  const tmp = new Float32Array(16);
  for (let c = 0; c < 4; c++) {
    for (let r = 0; r < 4; r++) {
      tmp[c * 4 + r] =
        a[r] * b[c * 4] +
        a[4 + r] * b[c * 4 + 1] +
        a[8 + r] * b[c * 4 + 2] +
        a[12 + r] * b[c * 4 + 3];
    }
  }
  out.set(tmp);
  return out;
}

export function mat4Perspective(out: Mat4, fovY: number, aspect: number, near: number, far: number): Mat4 {
  const f = 1.0 / Math.tan(fovY / 2);
  const nf = 1.0 / (near - far);
  out.fill(0);
  out[0] = f / aspect;
  out[5] = f;
  out[10] = (far + near) * nf;
  out[11] = -1;
  out[14] = 2 * far * near * nf;
  return out;
}

export function mat4LookAt(out: Mat4, eye: Vec3, center: Vec3, up: Vec3): Mat4 {
  const z = vec3(0, 0, 0);
  vec3Sub(z, eye, center);
  vec3Normalize(z, z);

  const x = vec3(0, 0, 0);
  vec3Cross(x, up, z);
  vec3Normalize(x, x);

  const y = vec3(0, 0, 0);
  vec3Cross(y, z, x);

  out[0] = x[0]; out[1] = y[0]; out[2] = z[0]; out[3] = 0;
  out[4] = x[1]; out[5] = y[1]; out[6] = z[1]; out[7] = 0;
  out[8] = x[2]; out[9] = y[2]; out[10] = z[2]; out[11] = 0;
  out[12] = -vec3Dot(x, eye);
  out[13] = -vec3Dot(y, eye);
  out[14] = -vec3Dot(z, eye);
  out[15] = 1;
  return out;
}

export function mat4Translate(out: Mat4, m: Mat4, v: Vec3): Mat4 {
  const vx = v[0], vy = v[1], vz = v[2];
  if (out !== m) out.set(m);
  out[12] = m[0] * vx + m[4] * vy + m[8] * vz + m[12];
  out[13] = m[1] * vx + m[5] * vy + m[9] * vz + m[13];
  out[14] = m[2] * vx + m[6] * vy + m[10] * vz + m[14];
  out[15] = m[3] * vx + m[7] * vy + m[11] * vz + m[15];
  return out;
}

export function mat4RotateY(out: Mat4, m: Mat4, angle: number): Mat4 {
  const s = Math.sin(angle), c = Math.cos(angle);
  const m0 = m[0], m1 = m[1], m2 = m[2], m3 = m[3];
  const m8 = m[8], m9 = m[9], m10 = m[10], m11 = m[11];
  if (out !== m) out.set(m);
  out[0] = m0 * c - m8 * s;
  out[1] = m1 * c - m9 * s;
  out[2] = m2 * c - m10 * s;
  out[3] = m3 * c - m11 * s;
  out[8] = m0 * s + m8 * c;
  out[9] = m1 * s + m9 * c;
  out[10] = m2 * s + m10 * c;
  out[11] = m3 * s + m11 * c;
  return out;
}

export function mat4Scale(out: Mat4, m: Mat4, v: Vec3): Mat4 {
  const vx = v[0], vy = v[1], vz = v[2];
  for (let i = 0; i < 4; i++) {
    out[i] = m[i] * vx;
    out[4 + i] = m[4 + i] * vy;
    out[8 + i] = m[8 + i] * vz;
    out[12 + i] = m[12 + i];
  }
  return out;
}

export function mat4Invert(out: Mat4, a: Mat4): Mat4 | null {
  const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
  const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
  const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
  const a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
  const b00 = a00 * a11 - a01 * a10;
  const b01 = a00 * a12 - a02 * a10;
  const b02 = a00 * a13 - a03 * a10;
  const b03 = a01 * a12 - a02 * a11;
  const b04 = a01 * a13 - a03 * a11;
  const b05 = a02 * a13 - a03 * a12;
  const b06 = a20 * a31 - a21 * a30;
  const b07 = a20 * a32 - a22 * a30;
  const b08 = a20 * a33 - a23 * a30;
  const b09 = a21 * a32 - a22 * a31;
  const b10 = a21 * a33 - a23 * a31;
  const b11 = a22 * a33 - a23 * a32;
  let det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
  if (Math.abs(det) < 1e-10) return null;
  det = 1.0 / det;
  out[0] = (a11 * b11 - a12 * b10 + a13 * b09) * det;
  out[1] = (a02 * b10 - a01 * b11 - a03 * b09) * det;
  out[2] = (a31 * b05 - a32 * b04 + a33 * b03) * det;
  out[3] = (a22 * b04 - a21 * b05 - a23 * b03) * det;
  out[4] = (a12 * b08 - a10 * b11 - a13 * b07) * det;
  out[5] = (a00 * b11 - a02 * b08 + a03 * b07) * det;
  out[6] = (a32 * b02 - a30 * b05 - a33 * b01) * det;
  out[7] = (a20 * b05 - a22 * b02 + a23 * b01) * det;
  out[8] = (a10 * b10 - a11 * b08 + a13 * b06) * det;
  out[9] = (a01 * b08 - a00 * b10 - a03 * b06) * det;
  out[10] = (a30 * b04 - a31 * b02 + a33 * b00) * det;
  out[11] = (a21 * b02 - a20 * b04 - a23 * b00) * det;
  out[12] = (a11 * b07 - a10 * b09 - a12 * b06) * det;
  out[13] = (a00 * b09 - a01 * b07 + a02 * b06) * det;
  out[14] = (a31 * b01 - a30 * b03 - a32 * b00) * det;
  out[15] = (a20 * b03 - a21 * b01 + a22 * b00) * det;
  return out;
}

export function quatToMat4(out: Mat4, q: number[]): Mat4 {
  const x = q[0], y = q[1], z = q[2], w = q[3];
  const x2 = x + x, y2 = y + y, z2 = z + z;
  const xx = x * x2, xy = x * y2, xz = x * z2;
  const yy = y * y2, yz = y * z2, zz = z * z2;
  const wx = w * x2, wy = w * y2, wz = w * z2;
  out[0] = 1 - (yy + zz); out[4] = xy - wz;       out[8]  = xz + wy;       out[12] = 0;
  out[1] = xy + wz;        out[5] = 1 - (xx + zz); out[9]  = yz - wx;       out[13] = 0;
  out[2] = xz - wy;        out[6] = yz + wx;        out[10] = 1 - (xx + yy); out[14] = 0;
  out[3] = 0;              out[7] = 0;              out[11] = 0;             out[15] = 1;
  return out;
}
