"""FPLP Language - Graphics / Image Processing Module (Pillow backend)"""

import os
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None


class FPLPImage:
    """Wrapper around PIL Image for FPLP."""
    def __init__(self, pil_image):
        self._img = pil_image

    @property
    def width(self):
        return self._img.width

    @property
    def height(self):
        return self._img.height

    @property
    def mode(self):
        return self._img.mode

    def __str__(self):
        return f"<Image {self.width}x{self.height} {self.mode}>"

    def __repr__(self):
        return self.__str__()


def _ensure_pillow():
    if Image is None:
        raise FPLPError("Pillow library not installed. Run: pip install Pillow")


# --- Builtin wrappers ---

def _create_image(args):
    """create_image(width, height, color='black')"""
    _ensure_pillow()
    w, h = int(args[0]), int(args[1])
    color = args[2] if len(args) > 2 else 'black'
    img = Image.new('RGBA', (w, h), color)
    return FPLPImage(img)


def _load_image(args):
    """load_image(path)"""
    _ensure_pillow()
    path = args[0]
    if not os.path.exists(path):
        raise FPLPError(f"image file not found: {path}")
    pil = Image.open(path).convert('RGBA')
    return FPLPImage(pil)


def _save_image(args):
    """save_image(img, path)"""
    _ensure_pillow()
    lpp_img = args[0]
    path = args[1]
    if not isinstance(lpp_img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    lpp_img._img.save(path)
    return None


def _image_width(args):
    """image_width(img)"""
    img = args[0]
    if not isinstance(img, FPLPImage):
        raise FPLPError("argument must be an image object")
    return img.width


def _image_height(args):
    """image_height(img)"""
    img = args[0]
    if not isinstance(img, FPLPImage):
        raise FPLPError("argument must be an image object")
    return img.height


def _resize(args):
    """resize(img, width, height)"""
    _ensure_pillow()
    img = args[0]
    w, h = int(args[1]), int(args[2])
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    new = img._img.resize((w, h), Image.LANCZOS)
    return FPLPImage(new)


def _crop(args):
    """crop(img, x, y, width, height)"""
    _ensure_pillow()
    img = args[0]
    x, y, w, h = int(args[1]), int(args[2]), int(args[3]), int(args[4])
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    new = img._img.crop((x, y, x + w, y + h))
    return FPLPImage(new)


def _draw_rect(args):
    """draw_rect(img, x, y, width, height, color='red', fill=True)"""
    _ensure_pillow()
    img = args[0]
    x, y, w, h = int(args[1]), int(args[2]), int(args[3]), int(args[4])
    color = args[5] if len(args) > 5 else 'red'
    fill = args[6] if len(args) > 6 else True
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    draw = ImageDraw.Draw(img._img)
    if fill:
        draw.rectangle([x, y, x + w, y + h], fill=color, outline=color)
    else:
        draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
    return None


def _draw_circle(args):
    """draw_circle(img, cx, cy, radius, color='red', fill=True)"""
    _ensure_pillow()
    img = args[0]
    cx, cy, r = int(args[1]), int(args[2]), int(args[3])
    color = args[4] if len(args) > 4 else 'red'
    fill = args[5] if len(args) > 5 else True
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    draw = ImageDraw.Draw(img._img)
    bbox = [cx - r, cy - r, cx + r, cy + r]
    if fill:
        draw.ellipse(bbox, fill=color, outline=color)
    else:
        draw.ellipse(bbox, outline=color, width=2)
    return None


def _draw_text(args):
    """draw_text(img, x, y, text, size=20, color='white')"""
    _ensure_pillow()
    img = args[0]
    x, y = int(args[1]), int(args[2])
    text = str(args[3])
    size = int(args[4]) if len(args) > 4 else 20
    color = args[5] if len(args) > 5 else 'white'
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    draw = ImageDraw.Draw(img._img)
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except (OSError, IOError):
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)
    return None


def _fill(args):
    """fill(img, color)"""
    _ensure_pillow()
    img = args[0]
    color = args[1]
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    draw = ImageDraw.Draw(img._img)
    draw.rectangle([0, 0, img.width, img.height], fill=color)
    return None


def _paste(args):
    """paste(dest_img, src_img, x, y)"""
    _ensure_pillow()
    dest = args[0]
    src = args[1]
    x, y = int(args[2]), int(args[3])
    if not isinstance(dest, FPLPImage):
        raise FPLPError("first argument must be an image object")
    if not isinstance(src, FPLPImage):
        raise FPLPError("second argument must be an image object")
    dest._img.paste(src._img, (x, y), src._img)
    return None


def _blur(args):
    """blur(img, radius=5)"""
    _ensure_pillow()
    img = args[0]
    radius = float(args[1]) if len(args) > 1 else 5.0
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    new = img._img.filter(ImageFilter.GaussianBlur(radius))
    return FPLPImage(new)


def _grayscale(args):
    """grayscale(img)"""
    _ensure_pillow()
    img = args[0]
    if not isinstance(img, FPLPImage):
        raise FPLPError("argument must be an image object")
    new = img._img.convert('L').convert('RGBA')
    return FPLPImage(new)


def _rotate(args):
    """rotate(img, degrees)"""
    _ensure_pillow()
    img = args[0]
    deg = float(args[1])
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    new = img._img.rotate(deg, expand=True)
    return FPLPImage(new)


def _flip(args):
    """flip(img, 'horizontal'|'vertical')"""
    _ensure_pillow()
    img = args[0]
    direction = str(args[1]) if len(args) > 1 else 'horizontal'
    if not isinstance(img, FPLPImage):
        raise FPLPError("first argument must be an image object")
    if direction == 'horizontal':
        new = img._img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        new = img._img.transpose(Image.FLIP_TOP_BOTTOM)
    return FPLPImage(new)


def _show_image(args):
    """show_image(img) — open image in default viewer + archive for GUI"""
    _ensure_pillow()
    img = args[0]
    if not isinstance(img, FPLPImage):
        raise FPLPError("argument must be an image object")

    # Archive for GUI display (grabs a copy)
    try:
        from .gui import get_image_archive
        get_image_archive().add(img._img.copy())
    except (ImportError, Exception):
        pass

    img._img.show()
    return None


# --- Registration ---
from .builtins import BuiltinFunction, FPLPError

GRAPHICS_FUNCS = {
    "create_image": BuiltinFunction("create_image", _create_image, min_args=2, max_args=3),
    "load_image": BuiltinFunction("load_image", _load_image, min_args=1, max_args=1),
    "save_image": BuiltinFunction("save_image", _save_image, min_args=2, max_args=2),
    "image_width": BuiltinFunction("image_width", _image_width, min_args=1, max_args=1),
    "image_height": BuiltinFunction("image_height", _image_height, min_args=1, max_args=1),
    "resize": BuiltinFunction("resize", _resize, min_args=3, max_args=3),
    "crop": BuiltinFunction("crop", _crop, min_args=5, max_args=5),
    "draw_rect": BuiltinFunction("draw_rect", _draw_rect, min_args=5, max_args=7),
    "draw_circle": BuiltinFunction("draw_circle", _draw_circle, min_args=4, max_args=6),
    "draw_text": BuiltinFunction("draw_text", _draw_text, min_args=4, max_args=6),
    "fill": BuiltinFunction("fill", _fill, min_args=2, max_args=2),
    "paste": BuiltinFunction("paste", _paste, min_args=4, max_args=4),
    "blur": BuiltinFunction("blur", _blur, min_args=1, max_args=2),
    "grayscale": BuiltinFunction("grayscale", _grayscale, min_args=1, max_args=1),
    "rotate": BuiltinFunction("rotate", _rotate, min_args=2, max_args=2),
    "flip": BuiltinFunction("flip", _flip, min_args=1, max_args=2),
    "show_image": BuiltinFunction("show_image", _show_image, min_args=1, max_args=1),
}
