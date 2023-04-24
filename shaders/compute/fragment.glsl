#version 330

uniform sampler2D texture0;
out vec4 fragColor;
uniform vec2 mouse;

// Check if something is living in the cell
bool cell(vec4 fragment) {
    return length(fragment.xyz) > 0.1;
}

void main() {
    // Get the pixel position we are currently writing
    ivec2 pos = ivec2(gl_FragCoord.xy);
    if (length(pos-mouse) < 5) {
		fragColor = vec4(1.0);
		return;
    }

    // Grab neighbor fragments + current one
    vec4 v1 = texelFetch(texture0, pos + ivec2(-1, -1), 0);
    vec4 v2 = texelFetch(texture0, pos + ivec2( 0, -1), 0);
    vec4 v3 = texelFetch(texture0, pos + ivec2( 1, -1), 0);

    vec4 v4 = texelFetch(texture0, pos + ivec2(-1, 0), 0);
    vec4 v5 = texelFetch(texture0, pos, 0);
    vec4 v6 = texelFetch(texture0, pos + ivec2(1,  0), 0);

    vec4 v7 = texelFetch(texture0, pos + ivec2(-1, 1), 0);
    vec4 v8 = texelFetch(texture0, pos + ivec2( 0, 1), 0);
    vec4 v9 = texelFetch(texture0, pos + ivec2( 1, 1), 0);

    // Cell in current position is alive?
    bool living = cell(v5);

    // Count how many neighbors is alive
    int neighbors = 0;
    if (cell(v1)) neighbors++;
    if (cell(v2)) neighbors++;
    if (cell(v3)) neighbors++;
    if (cell(v4)) neighbors++;
    if (cell(v6)) neighbors++;
    if (cell(v7)) neighbors++;
    if (cell(v8)) neighbors++;
    if (cell(v9)) neighbors++;

    // Average color for all neighbors
    vec4 sum = (v1 + v2 + v3 + v4 + v6 + v7 + v8 + v9) / float(neighbors);

    if (living) {
        if (neighbors == 2 || neighbors == 3) {
            // The cell lives, but we write out the average color minus a small value
            fragColor = vec4(sum.rgb - vec3(1.0/255.0), 1.0);
        } else {
            // The cell dies when too few or too many neighbors
            fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        }
    } else {
        if (neighbors == 3) {
            // A new cell was born
            fragColor = vec4(normalize(sum.rgb), 1.0);
        } else {
            // Still dead
            fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        }
    }
}
