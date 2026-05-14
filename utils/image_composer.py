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
    font_path: str = "arial.ttf"
) -> None:

    tw, th = template.size

    # Box testo in pixel
    box_w = int(tw * box_w_pct / 100)
    box_h = int(th * box_h_pct / 100)

    # Centro box
    center_x = int(tw * x_pct / 100)
    center_y = int(th * y_pct / 100)

    # Top-left box
    box_x = center_x - box_w // 2
    box_y = center_y - box_h // 2

    draw = ImageDraw.Draw(template)

    # Font iniziale
    font_size = box_h

    while font_size > 1:

        font = ImageFont.truetype(
            font_path,
            font_size
        )

        bbox = draw.textbbox(
            (0, 0),
            testo,
            font=font
        )

        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Se il testo entra nel box -> stop
        if text_w <= box_w and text_h <= box_h:
            break

        font_size -= 1

    # Coordinate centrate nel box
    x = box_x + (box_w - text_w) // 2
    y = box_y + (box_h - text_h) // 2

    draw.text(
        (x, y),
        testo,
        fill=colore,
        font=font
    )

def componi_immagine(
    template_bytes: bytes,
    product: ProductConfig,
    price: TextConfig | None = None
) -> BytesIO:

    template = Image.open(BytesIO(template_bytes)).convert("RGBA")

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

    if not price:
        price = TextConfig("PREZZO", 50, 50, 100, 100)

    if price:
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

    output = BytesIO()

    template.convert("RGB").save(
        output,
        format="JPEG",
        quality=90
    )

    output.seek(0)
    return output

def leggi_dimensioni_template(template_bytes: bytes) -> tuple[int, int]:
    """Ritorna (width, height) del template."""
    img = Image.open(BytesIO(template_bytes))
    return img.size  # (w, h)