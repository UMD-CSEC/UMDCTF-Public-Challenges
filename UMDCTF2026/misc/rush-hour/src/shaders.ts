export const BG_VERT = `
attribute vec2 a_position;
varying vec2 v_uv;
void main() {
  v_uv = a_position * 0.5 + 0.5;
  v_uv.y = 1.0 - v_uv.y;
  gl_Position = vec4(a_position, 0.9999, 1.0);
}`;

export const BG_FRAG = `
precision mediump float;
varying vec2 v_uv;
uniform sampler2D u_tex;
void main() {
  gl_FragColor = texture2D(u_tex, v_uv);
}`;

export const BLIT_VERT = `
attribute vec2 a_position;
varying vec2 v_uv;
void main() {
  v_uv = a_position * 0.5 + 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}`;

export const CAR_VERT = `
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_texcoord;
uniform mat4 u_mvp;
uniform mat4 u_model;
varying vec2 v_uv;
varying vec3 v_normal;
void main() {
  v_uv = a_texcoord;
  v_normal = mat3(u_model) * a_normal;
  gl_Position = u_mvp * vec4(a_position, 1.0);
}`;

export const CAR_FRAG = `
precision mediump float;
varying vec2 v_uv;
varying vec3 v_normal;
uniform sampler2D u_tex;
uniform vec3 u_lightDir;
void main() {
  vec4 col = texture2D(u_tex, v_uv);
  vec3 n = normalize(v_normal);
  float diff = max(dot(n, u_lightDir), 0.0);
  float light = 0.45 + 0.55 * diff;
  gl_FragColor = vec4(col.rgb * light, 1.0);
}`;
