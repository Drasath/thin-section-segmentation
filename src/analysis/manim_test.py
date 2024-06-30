from manim import *

class SegmentScene(Scene):
    def construct(self):
        shape = Square(4)
        self.play(Create(shape))
        
        # Divide the square into 4 segments using a grid
        grid = NumberPlane( x_range=[-2, 2, 2], y_range=[-2, 2, 2])
        
        self.play(Create(grid))


scene = SegmentScene()
scene.render()