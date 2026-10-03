// NEXUS-PRESENCE: RF Wave Pulse Shader
// Author: Uday Kiran Jammula

#ifdef GL_ES
precision mediump float;
#endif

uniform float u_time;
uniform vec2 u_resolution;
uniform vec3 u_color;

varying vec2 vUv;

void main() {
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(vUv, center);
    
    // Expanding concentric wave ripples
    float wave = sin(dist * 35.0 - u_time * 6.0);
    float alpha = smoothstep(0.48, 0.5, 1.0 - dist) * smoothstep(0.0, 0.2, wave);
    
    gl_FragColor = vec4(u_color, alpha * 0.7);
}
