"""
Game of Life - Shader Version

We're doing this in in a simple way drawing to textures.
We need two textures. One to keep the old state and
another to draw the new state into. These textures are
flipped around every frame.

This version of Game of Life also use colors. Dominant
colonies will keep spreading their color.

Press SPACE to generate new initial data

The cell and window size can be tweaked in the parameters below.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.game_of_life_colors
"""
import random
from array import array

from arcade import key
import arcade
from arcade.gl import geometry
from contextlib import contextmanager

WINDOW_WIDTH = 1024  # Width of the window
WINDOW_HEIGHT = 512  # Height of the window
FRAME_DELAY = 2  # The game will only update every 2th frame



class MouseState:
    pos: tuple[float, float]
    clicked: bool

    def __init__(self):
        self.pos = -0, -0
        self.clicked = False

    def track(self, x: float, y: float):
        if self.clicked:
            self.pos = x, y

    def clickdown(self, x, y):
        self.clicked = True
        self.pos = x, y

    def clickup(self):
        self.clicked = False
        self.pos = 0, 0 

class GameOfLife(arcade.Window):

    def __init__(self, width, height):
        super().__init__(
            width, height, "Game of Life - Shader Version", 
            fullscreen=False,
        )
        self.frame = 0

        # Configure the size of the playfield (cells)
        self.size = width , height
        # Create two textures for the next and previous state (RGB textures)
        self.texture_1 = self.ctx.texture(
            self.size,
            components=3,
            filter=(self.ctx.NEAREST, self.ctx.NEAREST),
        )
        self.texture_2 = self.ctx.texture(
            self.size,
            components=3,
            filter=(self.ctx.NEAREST, self.ctx.NEAREST)
        )
        self.write_initial_state()

        # Add the textures to framebuffers so we can render to them
        self.fbo_1 = self.ctx.framebuffer(color_attachments=[self.texture_1])
        self.fbo_2 = self.ctx.framebuffer(color_attachments=[self.texture_2])


        # Fullscreen quad (using triangle strip)
        self.quad_fs = geometry.quad_2d_fs()

        # Shader to draw the texture
        self.display_program = self.ctx.load_program(
            vertex_shader="shaders/render/vertex.glsl", 
            fragment_shader="shaders/render/fragment.glsl",
        )

        # Shader for creating the next game state.
        # It takes the previous state as input (texture0)
        # and renders the next state directly into the second texture.
        self.life_program = self.ctx.load_program(
            vertex_shader="shaders/compute/vertex.glsl",
            fragment_shader="shaders/compute/fragment.glsl",
        )

        self.mouse_controls = MouseState()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_controls.clickdown(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_controls.clickup()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_controls.track(x, y)

    def gen_initial_data(self, num_values: int):
        """
        Generate initial data. We need to be careful about the initial state.
        Just throwing in lots of random numbers will make the entire system
        die in a few frames. We need to give enough room for life to exist.

        This might be the slowest possible way we would generate the initial
        data, but it works for this example :)
        """
        choices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 64, 128, 192, 255]
        for i in range(num_values):
            yield random.choice(choices)

    def write_initial_state(self):
        """Write initial data to the source texture"""
        self.texture_1.write(array('B', self.gen_initial_data(self.size[0] * self.size[1] * 3)))
        

    @contextmanager
    def compute_context(self):
        self.fbo_2.use()
        self.texture_1.use()
        yield

    @contextmanager
    def store_previous(self):
        self.fbo_1.use()
        self.texture_2.use()
        yield

    @contextmanager
    def display_context(self):
        self.ctx.screen.use()
        self.texture_2.use()
        yield

    def on_draw(self):
        # Draw Texture
        with self.display_context():
            self.quad_fs.render(self.display_program)  # Display the texture
        
    def on_update(self, delta_time: float):
        self.life_program["mouse"] = self.mouse_controls.pos

        # Calculate the next state, put it in texture 2
        with self.compute_context():
            self.quad_fs.render(self.life_program)  # Run the life program
        
        # Copy the next state from texture 2 into texture 1 ready for next frame
        with self.store_previous():
            self.quad_fs.render(self.display_program)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.SPACE:
            self.write_initial_state()

    


GameOfLife(WINDOW_WIDTH, WINDOW_HEIGHT).run()
