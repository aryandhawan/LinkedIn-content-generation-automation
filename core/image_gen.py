from PIL import Image, ImageDraw, ImageFont
import textwrap

W, H = 1200, 1200

BG_COLOR = (245, 242, 235)     # warm off-white
LINE_COLOR = (30, 30, 30)
TEXT_COLOR = (20, 20, 20)
LABEL_COLOR = (120, 115, 105)
FOOTER_COLOR = (140, 135, 125)

BRAND_NAME = "TANDEM AI LABS"
WEBSITE = "tandem-ai.tech"


def get_fonts():
    try:
        serif_bold = ImageFont.truetype("georgiab.ttf", 58)
        regular = ImageFont.truetype("georgia.ttf", 26)
    except:
        serif_bold = ImageFont.load_default()
        regular = ImageFont.load_default()
    return serif_bold, regular


def generate_poster(headline: str, save_path: str = "linkedin_poster_editorial.png") -> str:
    serif_bold, regular = get_fonts()

    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.text((90, 90), BRAND_NAME, font=regular, fill=LABEL_COLOR)
    draw.line([(90, 140), (300, 140)], fill=LINE_COLOR, width=2)

    wrapped = textwrap.fill(headline, width=20)
    draw.multiline_text((90, 420), wrapped, font=serif_bold, fill=TEXT_COLOR, spacing=18)

    draw.text((90, H - 100), WEBSITE, font=regular, fill=FOOTER_COLOR)

    img.save(save_path)
    return save_path


if __name__ == "__main__":
    path = generate_poster("Why most businesses over-engineer their first AI automation")
    print(f"Saved to: {path}")
    from PIL import Image as PILImage
    PILImage.open(path).show()


