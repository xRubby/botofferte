from PIL import Image
from io import BytesIO
import requests

def componi_immagine(
    template_bytes: bytes,
    product_img_url: str,
    prod_x_pct: int,
    prod_y_pct: int,
    prod_w_pct: int,
    prod_h_pct: int
) -> BytesIO:
    template = Image.open(BytesIO(template_bytes)).convert("RGBA")
    tw, th = template.size

    resp = requests.get(product_img_url, timeout=10)
    resp.raise_for_status()
    prodotto = Image.open(BytesIO(resp.content)).convert("RGBA")

    # Box in px calcolato dal template
    prod_w = int(tw * prod_w_pct / 100)
    prod_h = int(th * prod_h_pct / 100)

    # Ridimensiona proporzionalmente per stare nel box
    ratio = min(prod_w / prodotto.width, prod_h / prodotto.height)
    new_w = int(prodotto.width * ratio)
    new_h = int(prodotto.height * ratio)
    prodotto = prodotto.resize((new_w, new_h), Image.LANCZOS)
    pw, ph = prodotto.size

    # Calcola angolo top-left centrando nel box
    box_x = int((prod_x_pct / 100) * tw - prod_w / 2)
    box_y = int((prod_y_pct / 100) * th - prod_h / 2)

    x = box_x + (prod_w - pw) // 2
    y = box_y + (prod_h - ph) // 2

    x = max(0, min(x, tw - pw))
    y = max(0, min(y, th - ph))

    template.paste(prodotto, (x, y), prodotto)

    output = BytesIO()
    template.convert("RGB").save(output, format="JPEG", quality=90)
    output.seek(0)
    return output


def leggi_dimensioni_template(template_bytes: bytes) -> tuple[int, int]:
    """Ritorna (width, height) del template."""
    img = Image.open(BytesIO(template_bytes))
    return img.size  # (w, h)