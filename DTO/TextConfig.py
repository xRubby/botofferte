from dataclasses import dataclass

@dataclass
class TextConfig:
    text: str
    x_pct: int
    y_pct: int
    box_w_pct: int
    box_h_pct: int
    color: str = "black"
    font_path: str = "arial.ttf"