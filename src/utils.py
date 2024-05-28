import math
from widgets import base_font
from tkinter.font import Font as tkFont

def get_scaled_font(width: int, breakpoint: int) -> tkFont:
    font_size = 18 if width > breakpoint else math.floor(18 * (width / breakpoint))
    
    return base_font if font_size == 18 else tkFont(family="Lucida Console", size=font_size, weight="normal")