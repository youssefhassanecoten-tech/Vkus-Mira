# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.utils import simpleSplit

sys.path.insert(0, str(Path(__file__).parent))
from recipes_data import RECIPES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "pdfs"
OUT_DIR.mkdir(exist_ok=True)

PAPER = HexColor("#FFFCF6")
INK = HexColor("#231C16")
MUTED = HexColor("#6E5C4C")
SOFT = HexColor("#927D68")
LINE = HexColor("#E8DAC8")
CREAM = HexColor("#FBF6EE")

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", "C:/Windows/Fonts/arialbi.ttf"))
pdfmetrics.registerFontFamily(
    "Arial",
    normal="Arial",
    bold="Arial-Bold",
    italic="Arial-Italic",
    boldItalic="Arial-BoldItalic",
)

BASE = getSampleStyleSheet()

STYLES = {
    "kicker": ParagraphStyle(
        "kicker",
        fontName="Arial-Bold",
        fontSize=7.5,
        leading=10,
        textColor=SOFT,
        spaceAfter=2,
    ),
    "h1": ParagraphStyle(
        "h1",
        fontName="Arial-Bold",
        fontSize=25,
        leading=28,
        textColor=INK,
        spaceAfter=3,
    ),
    "subtitle": ParagraphStyle(
        "subtitle",
        fontName="Arial-Italic",
        fontSize=11.5,
        leading=15,
        textColor=MUTED,
        spaceAfter=8,
    ),
    "lead": ParagraphStyle(
        "lead",
        fontName="Arial",
        fontSize=10.5,
        leading=15.2,
        textColor=INK,
        spaceAfter=8,
    ),
    "body": ParagraphStyle(
        "body",
        fontName="Arial",
        fontSize=9.7,
        leading=13.8,
        textColor=INK,
        spaceAfter=4,
    ),
    "small": ParagraphStyle(
        "small",
        fontName="Arial",
        fontSize=8.7,
        leading=12,
        textColor=MUTED,
        spaceAfter=3,
    ),
    "tiny": ParagraphStyle(
        "tiny",
        fontName="Arial",
        fontSize=7.5,
        leading=10,
        textColor=SOFT,
    ),
    "h2": ParagraphStyle(
        "h2",
        fontName="Arial-Bold",
        fontSize=14.5,
        leading=18,
        textColor=INK,
        spaceBefore=2,
        spaceAfter=2,
    ),
    "h3": ParagraphStyle(
        "h3",
        fontName="Arial-Bold",
        fontSize=10.5,
        leading=14,
        textColor=INK,
        spaceAfter=3,
    ),
    "bullet": ParagraphStyle(
        "bullet",
        fontName="Arial",
        fontSize=9.4,
        leading=13.2,
        textColor=INK,
        leftIndent=10,
        bulletIndent=0,
        spaceAfter=2.3,
    ),
    "bullet_small": ParagraphStyle(
        "bullet_small",
        fontName="Arial",
        fontSize=8.8,
        leading=12.2,
        textColor=INK,
        leftIndent=9,
        bulletIndent=0,
        spaceAfter=2,
    ),
    "ingredient": ParagraphStyle(
        "ingredient",
        fontName="Arial",
        fontSize=9.2,
        leading=12.2,
        textColor=INK,
        leftIndent=8,
        bulletIndent=0,
        spaceAfter=3,
    ),
    "stage_title": ParagraphStyle(
        "stage_title",
        fontName="Arial-Bold",
        fontSize=11.2,
        leading=14,
        textColor=INK,
        spaceAfter=2,
    ),
    "stage_text": ParagraphStyle(
        "stage_text",
        fontName="Arial",
        fontSize=9.15,
        leading=12.7,
        textColor=INK,
    ),
    "badge": ParagraphStyle(
        "badge",
        fontName="Arial-Bold",
        fontSize=12.5,
        leading=15,
        textColor=colors.white,
        alignment=TA_CENTER,
    ),
    "meta_label": ParagraphStyle(
        "meta_label",
        fontName="Arial-Bold",
        fontSize=6.8,
        leading=9,
        textColor=SOFT,
        alignment=TA_LEFT,
    ),
    "meta_value": ParagraphStyle(
        "meta_value",
        fontName="Arial-Bold",
        fontSize=10.2,
        leading=13,
        textColor=INK,
        alignment=TA_LEFT,
    ),
    "table_head": ParagraphStyle(
        "table_head",
        fontName="Arial-Bold",
        fontSize=8.2,
        leading=10,
        textColor=colors.white,
    ),
    "table_body": ParagraphStyle(
        "table_body",
        fontName="Arial",
        fontSize=8.7,
        leading=11.5,
        textColor=INK,
    ),
    "table_time": ParagraphStyle(
        "table_time",
        fontName="Arial-Bold",
        fontSize=8.8,
        leading=11,
        textColor=INK,
    ),
    "quote": ParagraphStyle(
        "quote",
        fontName="Arial-Italic",
        fontSize=10.3,
        leading=15,
        textColor=INK,
    ),
    "credit": ParagraphStyle(
        "credit",
        fontName="Arial",
        fontSize=6.4,
        leading=8,
        textColor=SOFT,
    ),
    "quick": ParagraphStyle(
        "quick",
        fontName="Arial",
        fontSize=9.5,
        leading=13.2,
        textColor=INK,
        leftIndent=10,
        bulletIndent=0,
        spaceAfter=4,
    ),
}


def para(text, style="body", bullet=None):
    return Paragraph(escape(str(text)), STYLES[style], bulletText=bullet)


def shorten(text, sentences=2):
    parts = re.split(r"(?<=[.!?])\s+", str(text).strip())
    return " ".join(parts[:sentences]).strip()


def section_title(text, accent, kicker=None):
    out = [Spacer(1, 3.6 * mm)]
    if kicker:
        out.append(Paragraph(escape(kicker.upper()), STYLES["kicker"]))
    out.append(Paragraph(escape(text), STYLES["h2"]))
    out.append(
        HRFlowable(
            width="100%",
            thickness=0.65,
            color=HexColor(accent),
            spaceBefore=1,
            spaceAfter=3,
        )
    )
    return out


def meta_table(recipe, accent, content_width):
    m = recipe["meta"]
    labels = [
        ("ПОРЦИИ", m["portions"]),
        ("ПОДГОТОВКА", m["prep"]),
        ("ГОТОВКА", m["cook"]),
        ("СЛОЖНОСТЬ", m["difficulty"]),
        ("ОСТРОТА", m["spice"]),
    ]
    cells = []
    for label, value in labels:
        cells.append(
            [
                Paragraph(escape(label), STYLES["meta_label"]),
                Paragraph(escape(value), STYLES["meta_value"]),
            ]
        )
    table = Table([cells], colWidths=[content_width / 5.0] * 5, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor(recipe["accent_light"])),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, HexColor(recipe["accent_light"])),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def ingredient_markup(item):
    name = escape(item["name"])
    amount = escape(item["amount"])
    note = escape(item.get("note", "")).strip()
    text = f"<b>{name}</b> <font color='#7A6653'>— {amount}</font>"
    if note:
        text += f"<br/><font size='7.4' color='#927D68'>{note}</font>"
    return text


def ingredient_table(recipe, content_width):
    items = recipe["ingredients"]
    rows = []
    for i in range(0, len(items), 2):
        row = []
        for item in items[i : i + 2]:
            row.append(Paragraph(ingredient_markup(item), STYLES["ingredient"], bulletText="•"))
        if len(row) == 1:
            row.append("")
        rows.append(row)
    table = Table(rows, colWidths=[content_width / 2.0] * 2, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def shopping_table(recipe, content_width):
    head = [
        Paragraph("ГДЕ ИСКАТЬ", STYLES["table_head"]),
        Paragraph("ЧТО БРАТЬ", STYLES["table_head"]),
    ]
    rows = [head]
    for row in recipe["shopping"]:
        where = (
            f"<b>{escape(row['place'])}</b>"
            f"<br/><font size='7.2' color='#927D68'>{escape(row['address'])}</font>"
        )
        rows.append([Paragraph(where, STYLES["table_body"]), Paragraph(escape(row["what"]), STYLES["table_body"])])
    table = Table(rows, colWidths=[58 * mm, content_width - 58 * mm], hAlign="LEFT", repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor(recipe["accent_dark"])),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), CREAM))
    table.setStyle(TableStyle(style))
    return table


def timeline_table(recipe, content_width):
    rows = [[Paragraph("ВРЕМЯ", STYLES["table_head"]), Paragraph("ЧТО ДЕЛАЕМ", STYLES["table_head"])]]
    for t, what in recipe["timeline"]:
        rows.append([Paragraph(escape(t), STYLES["table_time"]), Paragraph(escape(what), STYLES["table_body"])])
    table = Table(rows, colWidths=[28 * mm, content_width - 28 * mm], hAlign="LEFT", repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor(recipe["accent_dark"])),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), CREAM))
    table.setStyle(TableStyle(style))
    return table


def prep_table(recipe, content_width):
    rows = []
    for i in range(0, len(recipe["prep"]), 2):
        row = []
        for item in recipe["prep"][i : i + 2]:
            text = f"<b>{escape(item['title'])}.</b> {escape(item['text'])}"
            row.append(Paragraph(text, STYLES["bullet_small"]))
        if len(row) == 1:
            row.append("")
        rows.append(row)
    table = Table(rows, colWidths=[content_width / 2.0] * 2, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def troubleshooting_table(recipe, content_width):
    rows = [[Paragraph("ЧТО ПОШЛО НЕ ТАК", STYLES["table_head"]), Paragraph("КАК ИСПРАВИТЬ", STYLES["table_head"])]]
    for item in recipe["troubleshooting"]:
        rows.append(
            [
                Paragraph(escape(item["problem"]), STYLES["table_body"]),
                Paragraph(escape(item["solution"]), STYLES["table_body"]),
            ]
        )
    table = Table(rows, colWidths=[content_width * 0.38, content_width * 0.62], hAlign="LEFT", repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor(recipe["accent_dark"])),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), CREAM))
    table.setStyle(TableStyle(style))
    return table


def stage_card(stage, recipe, content_width):
    badge = Paragraph(escape(stage["percent"]), STYLES["badge"])
    content = [
        Paragraph(escape(stage["title"]), STYLES["stage_title"]),
        Spacer(1, 1.5),
        Paragraph(escape(stage["text"]), STYLES["stage_text"]),
    ]
    card = Table([[badge, content]], colWidths=[18 * mm, content_width - 18 * mm], hAlign="LEFT")
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), HexColor(recipe["accent_dark"])),
                ("BACKGROUND", (1, 0), (1, 0), CREAM),
                ("BOX", (0, 0), (-1, -1), 0.55, HexColor(recipe["accent_light"])),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, 0), 3),
                ("RIGHTPADDING", (0, 0), (0, 0), 3),
                ("TOPPADDING", (0, 0), (0, 0), 9),
                ("BOTTOMPADDING", (0, 0), (0, 0), 9),
                ("LEFTPADDING", (1, 0), (1, 0), 8),
                ("RIGHTPADDING", (1, 0), (1, 0), 8),
                ("TOPPADDING", (1, 0), (1, 0), 5),
                ("BOTTOMPADDING", (1, 0), (1, 0), 6),
            ]
        )
    )
    return KeepTogether([Spacer(1, 1.7 * mm), card])


def callout(title, text, recipe, content_width):
    body = [
        Paragraph(escape(title.upper()), ParagraphStyle(
            "callout_title",
            fontName="Arial-Bold",
            fontSize=7.4,
            leading=10,
            textColor=HexColor(recipe["accent_dark"]),
        )),
        Spacer(1, 2),
        Paragraph(escape(text), STYLES["quote"]),
    ]
    table = Table([[body]], colWidths=[content_width], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                ("BOX", (0, 0), (-1, -1), 0.55, HexColor(recipe["accent_light"])),
                ("LINEBEFORE", (0, 0), (0, -1), 3, HexColor(recipe["accent"])),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def draw_image_cover(c, path, x, y, w, h):
    image = Image(str(path), width=w, height=h)
    image.drawOn(c, x, y)


def draw_wrapped(c, text, x, y, width, font, size, leading, color):
    c.setFillColor(color)
    c.setFont(font, size)
    lines = simpleSplit(text, font, size, width)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_cover(c, doc):
    recipe = doc.recipe
    w, h = A4
    accent = HexColor(recipe["accent"])
    accent_dark = HexColor(recipe["accent_dark"])
    accent_light = HexColor(recipe["accent_light"])
    margin = 20 * mm

    c.saveState()
    c.setFillColor(PAPER)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Very light geometric texture.
    c.setFillColor(accent_light)
    c.setFillAlpha(0.32)
    for i in range(7):
        for j in range(4):
            cx = w - 16 * mm - i * 5.2 * mm
            cy = 37 * mm + j * 5.2 * mm
            c.saveState()
            c.translate(cx, cy)
            c.rotate(45)
            c.rect(-1.5 * mm, -1.5 * mm, 3 * mm, 3 * mm, fill=1, stroke=0)
            c.restoreState()
    c.setFillAlpha(1)

    # Top labels.
    c.setFillColor(accent_dark)
    c.setFont("Arial-Bold", 8.5)
    c.drawString(margin, h - 23 * mm, "БЛИЖНИЙ ВОСТОК")
    c.setFillColor(MUTED)
    c.setFont("Arial", 7.5)
    c.drawString(margin, h - 29 * mm, f"{recipe.get('country_name', 'Египет').upper()} • САНКТ-ПЕТЕРБУРГ • 2026")

    # Huge number.
    c.setFillColor(accent_light)
    c.setFont("Arial-Bold", 74)
    c.drawRightString(w - margin, h - 39 * mm, recipe["num"])

    c.setFillColor(accent_dark)
    c.setFont("Arial-Bold", 7.5)
    c.drawString(margin, h - 51 * mm, "ПОЛНЫЙ ГИД 0–100")

    # Title.
    title_size = 38 if len(recipe["title"]) < 18 else 33
    title_lines = simpleSplit(recipe["title"], "Arial-Bold", title_size, 126 * mm)
    y = h - 66 * mm
    c.setFillColor(INK)
    c.setFont("Arial-Bold", title_size)
    for line in title_lines:
        c.drawString(margin, y, line)
        y -= title_size * 1.04

    y -= 4 * mm
    c.setFillColor(MUTED)
    c.setFont("Arial-Italic", 13)
    c.drawString(margin, y, recipe["subtitle"])
    y -= 8 * mm
    c.setFillColor(SOFT)
    c.setFont("Arial", 9.5)
    tag_lines = simpleSplit(recipe["tagline"], "Arial", 9.5, 135 * mm)
    for line in tag_lines[:2]:
        c.drawString(margin, y, line)
        y -= 12

    # Photo block.
    photo_x = margin
    photo_y = 25 * mm
    photo_w = w - 2 * margin
    photo_h = photo_w / 1.6
    photo_path = ROOT / recipe["photo"]
    if photo_path.exists():
        draw_image_cover(c, photo_path, photo_x, photo_y, photo_w, photo_h)
    else:
        c.setFillColor(accent_light)
        c.rect(photo_x, photo_y, photo_w, photo_h, fill=1, stroke=0)
    c.setStrokeColor(accent)
    c.setLineWidth(1.1)
    c.rect(photo_x, photo_y, photo_w, photo_h, fill=0, stroke=1)

    # Caption strip on photo.
    strip_h = 14 * mm
    c.setFillColor(accent_dark)
    c.setFillAlpha(0.94)
    c.rect(photo_x, photo_y, photo_w, strip_h, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setFillColor(colors.white)
    c.setFont("Arial-Bold", 8.2)
    c.drawString(photo_x + 6 * mm, photo_y + 5.5 * mm, "0–100 • ПОШАГОВЫЙ ГИД")
    c.setFont("Arial", 8.2)
    c.drawRightString(photo_x + photo_w - 6 * mm, photo_y + 5.5 * mm, recipe["meta"]["portions"].upper())

    # Credit and footer.
    c.setFillColor(SOFT)
    c.setFont("Arial", 6.5)
    c.drawString(margin, 19 * mm, recipe["photo_credit"])
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(margin, 15 * mm, w - margin, 15 * mm)
    c.setFillColor(MUTED)
    c.setFont("Arial", 7.3)
    c.drawString(margin, 10 * mm, "Санкт-Петербург • 2026")
    c.drawRightString(w - margin, 10 * mm, f"Ближний Восток • {len(RECIPES)} рецептов")
    c.restoreState()


def draw_content_page(c, doc):
    recipe = doc.recipe
    w, h = A4
    accent = HexColor(recipe["accent"])
    accent_dark = HexColor(recipe["accent_dark"])
    margin = 20 * mm

    c.saveState()
    c.setFillColor(PAPER)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Header.
    c.setFillColor(accent)
    c.rect(margin, h - 17.4 * mm, 2.2 * mm, 2.2 * mm, fill=1, stroke=0)
    c.setFillColor(accent_dark)
    c.setFont("Arial-Bold", 7.5)
    c.drawString(margin + 4 * mm, h - 16.8 * mm, recipe["title"].upper())
    c.setFillColor(SOFT)
    c.setFont("Arial", 7)
    c.drawRightString(w - margin, h - 16.8 * mm, "БЛИЖНИЙ ВОСТОК • 0–100")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.line(margin, h - 19.5 * mm, w - margin, h - 19.5 * mm)

    # Footer.
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.line(margin, 14 * mm, w - margin, 14 * mm)
    c.setFillColor(SOFT)
    c.setFont("Arial", 6.8)
    c.drawString(margin, 9.3 * mm, "Санкт-Петербург • 2026")
    c.setFillColor(accent_dark)
    c.setFont("Arial-Bold", 7.4)
    c.drawRightString(w - margin, 9.3 * mm, f"стр. {doc.page}")
    c.restoreState()


def build_recipe(recipe):
    out_path = OUT_DIR / f"{recipe['num']}_{recipe['id']}.pdf"
    margin_x = 20 * mm
    top = 25 * mm
    bottom = 19 * mm
    frame_w = A4[0] - 2 * margin_x
    frame_h = A4[1] - top - bottom

    doc = BaseDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=top,
        bottomMargin=bottom,
        title=f"{recipe['title']} — полный гид 0–100",
        author="Вкус Ближнего Востока • Санкт-Петербург",
        subject="Ближний Восток: покупки, подготовка и пошаговый рецепт",
    )
    doc.recipe = recipe

    cover_frame = Frame(0, 0, A4[0], A4[1], leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    content_frame = Frame(margin_x, bottom, frame_w, frame_h, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="content", frames=[content_frame], onPage=draw_content_page),
        ]
    )

    accent = recipe["accent"]
    accent_dark = recipe["accent_dark"]
    accent_light = recipe["accent_light"]
    content_width = frame_w

    story = [NextPageTemplate("content"), PageBreak()]

    # Page 2: short intro, meta and ingredients.
    story.append(Paragraph("ПОЛНЫЙ ГИД 0–100", STYLES["kicker"]))
    story.append(Paragraph(escape(recipe["title"]), STYLES["h1"]))
    story.append(Paragraph(escape(recipe["subtitle"]), STYLES["subtitle"]))
    story.append(Paragraph(escape(shorten(recipe["description"], 2)), STYLES["lead"]))
    story.append(Spacer(1, 2 * mm))
    story.append(meta_table(recipe, accent, content_width))
    story.append(Spacer(1, 2 * mm))
    story += section_title("Что купить", accent, recipe["meta"]["portions"])
    story.append(ingredient_table(recipe, content_width))
    story.append(Spacer(1, 4 * mm))
    story += section_title("Подготовка", accent, "Что сделать заранее")
    story.append(prep_table(recipe, content_width))
    story.append(PageBreak())

    # Page 3: shopping, then steps.
    story += section_title("Где купить в Санкт-Петербурге", accent, "Практичный маршрут")
    story.append(shopping_table(recipe, content_width))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "Ассортимент и режим работы могут меняться. В восточных лавках у Апраксина двора и на Сенной "
        "стоит спрашивать запас на складе: на витрине есть не всё.",
        STYLES["tiny"],
    ))
    story.append(CondPageBreak(80 * mm))

    # Steps 0–100.
    story += section_title("Пошаговый гид 0–100", accent, "От пустой кастрюли до полной тарелки")
    story.append(Paragraph(
        "Одиннадцать остановок без воды: что делать, на что смотреть и когда пробовать. "
        "Проценты показывают, где вы находитесь.",
        STYLES["body"],
    ))
    story.append(Spacer(1, 1 * mm))
    for stage in recipe["stages"]:
        story.append(stage_card(stage, recipe, content_width))

    # Serving, storage and fixes.
    story.append(CondPageBreak(90 * mm))
    story += section_title("Подача", accent)
    for item in recipe["serving"]:
        story.append(para(item, "bullet", "•"))
    story.append(Spacer(1, 2.5 * mm))
    story += section_title("Хранение и разогрев", accent)
    for item in recipe["storage"]:
        story.append(para(item, "bullet", "•"))
    story.append(Spacer(1, 2.5 * mm))
    story += section_title("Если что-то пошло не так", accent, "Спокойно, это чинится")
    story.append(troubleshooting_table(recipe, content_width))

    doc.build(story)
    return out_path


def main():
    paths = []
    for recipe in RECIPES:
        p = build_recipe(recipe)
        paths.append(p)
        print(p.name)
    print(f"Done: {len(paths)} PDFs")


if __name__ == "__main__":
    main()
