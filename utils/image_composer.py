from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

from DTO.ProductConfig import ProductConfig
from DTO.TextConfig import TextConfig

def scarica_immagine(url: str) -> Image.Image:
    """Scarica un'immagine da URL e la converte in RGBA."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    return Image.open(BytesIO(resp.content)).convert("RGBA")


def ridimensiona_in_box(
    immagine: Image.Image,
    box_w: int,
    box_h: int
) -> Image.Image:
    """
    Ridimensiona proporzionalmente un'immagine
    per farla stare dentro un box.
    """
    ratio = min(box_w / immagine.width, box_h / immagine.height)

    new_w = int(immagine.width * ratio)
    new_h = int(immagine.height * ratio)

    return immagine.resize((new_w, new_h), Image.LANCZOS)


def incolla_immagine(
    template: Image.Image,
    immagine: Image.Image,
    center_x_pct: int,
    center_y_pct: int,
    box_w_pct: int,
    box_h_pct: int
) -> None:
    """
    Incolla un'immagine centrata in un box definito
    in percentuale rispetto al template.
    """
    tw, th = template.size

    # Dimensioni box in pixel
    box_w = int(tw * box_w_pct / 100)
    box_h = int(th * box_h_pct / 100)

    # Ridimensiona immagine
    immagine = ridimensiona_in_box(immagine, box_w, box_h)

    iw, ih = immagine.size

    # Top-left del box
    box_x = int((center_x_pct / 100) * tw - box_w / 2)
    box_y = int((center_y_pct / 100) * th - box_h / 2)

    # Centra l'immagine nel box
    x = box_x + (box_w - iw) // 2
    y = box_y + (box_h - ih) // 2

    # Clamp coordinate
    x = max(0, min(x, tw - iw))
    y = max(0, min(y, th - ih))

    template.paste(immagine, (x, y), immagine)


def scrivi_testo(
    template: Image.Image,
    testo: str,
    x_pct: int,
    y_pct: int,
    box_w_pct: int,
    box_h_pct: int,
    colore: str = "black",
    font_path: str = "./fonts/Inter.ttc",
    align: str = "center",  # left | center | right
    barrato: bool = False,
    spessore_linea: int = 10
) -> None:

    tw, th = template.size

    # Box testo in pixel
    box_w = int(tw * box_w_pct / 100)
    box_h = int(th * box_h_pct / 100)

    # Centro box
    center_x = int(tw * x_pct / 100)
    center_y = int(th * y_pct / 100)

    draw = ImageDraw.Draw(template)

    # Font iniziale
    font_size = box_h
    font = None

    while font_size > 1:

        font = ImageFont.truetype(font_path, font_size)

        bbox = draw.textbbox(
            (0, 0),
            testo,
            font=font
        )

        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Se entra nel box -> stop
        if text_w <= box_w and text_h <= box_h:
            break

        font_size -= 1

    if font is None:
        return
    
        # Anchor orizzontale
    anchor_map = {
        "left": "ls",
        "center": "mm",
        "right": "rs"
    }

    anchor = anchor_map.get(
        align,
        "mm"
    )

    draw.text(
        (center_x, center_y),
        testo,
        fill=colore,
        font=font,
        anchor=anchor
    )
    # -------------------------
    # LINEA BARRATA
    # -------------------------
    if barrato:

        # bbox del testo reale centrato
        bbox = draw.textbbox(
            (center_x, center_y),
            testo,
            font=font,
            anchor=anchor
        )

        x1, y1, x2, y2 = bbox

        # posizione verticale della barra
        y_line = y1 + (y2 - y1) * 0.42

        draw.line(
            [(x1, y_line), (x2, y_line)],
            fill=colore,
            width=spessore_linea
        )

def componi_immagine(
    template_bytes: bytes,
    product: ProductConfig,
    price: TextConfig | None = None,
    oldprice: TextConfig | None = None,
    discount: TextConfig | None = None,
) -> BytesIO:

    template = Image.open(BytesIO(template_bytes)).convert("RGBA")

    #PER DEBUG
    #disegna_croce_centrale(template)

    prodotto = scarica_immagine(product.image_url)

    #Immagine prodotto
    incolla_immagine(
        template=template,
        immagine=prodotto,
        center_x_pct=product.x_pct,
        center_y_pct=product.y_pct,
        box_w_pct=product.w_pct,
        box_h_pct=product.h_pct
    )

    if price and price.active:
        scrivi_testo(
            template=template,
            testo=price.text,
            x_pct=price.x_pct,
            y_pct=price.y_pct,
            box_w_pct=price.box_w_pct,
            box_h_pct=price.box_h_pct,
            colore=price.color,
            font_path=price.font_path
        )
    
    if oldprice and oldprice.active:
        scrivi_testo(
            template=template,
            testo=oldprice.text,
            x_pct=oldprice.x_pct,
            y_pct=oldprice.y_pct,
            box_w_pct=oldprice.box_w_pct,
            box_h_pct=oldprice.box_h_pct,
            colore=oldprice.color,
            font_path=oldprice.font_path,
            barrato=True
        )
    
    if discount and discount.active:
        scrivi_testo(
            template=template,
            testo=discount.text,
            x_pct=discount.x_pct,
            y_pct=discount.y_pct,
            box_w_pct=discount.box_w_pct,
            box_h_pct=discount.box_h_pct,
            colore=discount.color,
            font_path=discount.font_path
        )

    output = BytesIO()

    template.convert("RGB").save(
        output,
        format="JPEG",
        quality=90
    )

    output.seek(0)
    return output

def disegna_croce_centrale(
    template: Image.Image,
    colore: str = "red",
    spessore: int = 2
) -> None:
    """
    Disegna una croce centrata sull'immagine:
    - linea orizzontale
    - linea verticale
    """
    draw = ImageDraw.Draw(template)

    w, h = template.size

    cx = w // 2
    cy = h // 2

    # Linea orizzontale
    draw.line(
        [(0, cy), (w, cy)],
        fill=colore,
        width=spessore
    )

    # Linea verticale
    draw.line(
        [(cx, 0), (cx, h)],
        fill=colore,
        width=spessore
    )

def leggi_dimensioni_template(template_bytes: bytes) -> tuple[int, int]:
    """Ritorna (width, height) del template."""
    img = Image.open(BytesIO(template_bytes))
    return img.size  # (w, h)