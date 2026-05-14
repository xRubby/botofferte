from dataclasses import dataclass

@dataclass
class ProductConfig:
    image_url: str
    x_pct: int
    y_pct: int
    w_pct: int
    h_pct: int