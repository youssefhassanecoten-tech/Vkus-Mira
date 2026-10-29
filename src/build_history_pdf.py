# -*- coding: utf-8 -*-
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))

INK = colors.HexColor("#211B16")
MUTED = colors.HexColor("#6F6154")
LINE = colors.HexColor("#E4D5C3")

HISTORY = [
    (
        "2.1.1",
        "29.10.2026",
        {
            "ru": ["Возвращены флаги стран в карточки.", "Исправлен визуальный регресс после версии 2.1.0."],
            "en": ["Restored country flags on the country cards.", "Fixed the visual regression introduced in version 2.1.0."],
        },
    ),
    (
        "2.1.0",
        "29.10.2026",
        {
            "ru": ["Убраны флаги с карточек стран.", "Возвращён фильтр «Все страны».", "Добавлены карточки сложных ингредиентов и альтернативы.", "Добавлены версия, история версий и двуязычные правовые страницы."],
            "en": ["Removed flags from country cards.", "Restored the All countries filter.", "Added complex-ingredient cards and alternatives.", "Added versioning, version history, and bilingual legal pages."],
        },
    ),
    (
        "2.0.0",
        "October 2026",
        {
            "ru": ["Проект расширен до 50 блюд Ближнего Востока.", "Пять кухонь: Египет, Ливан, Сирия, Турция и Палестина.", "Добавлены 50 компактных PDF-гидов.", "Добавлены лицензия и Privacy & Policy."],
            "en": ["Expanded to 50 Middle Eastern dishes.", "Five cuisines: Egypt, Lebanon, Syria, Turkey, and Palestine.", "Added 50 compact PDF guides.", "Added the license and Privacy & Policy."],
        },
    ),
    (
        "1.0.1",
        "2026",
        {
            "ru": ["Добавлена политика безопасности."],
            "en": ["Added the security policy."],
        },
    ),
    (
        "1.0.0",
        "2026",
        {
            "ru": ["Первый запуск приложения.", "10 египетских рецептов и PDF-гиды.", "Отметки ингредиентов, подготовки и готовки."],
            "en": ["Initial app release.", "10 Egyptian recipes and PDF guides.", "Ingredient, preparation, and cooking checkmarks."],
        },
    ),
]


def build(lang, out_name):
    ru = lang == "ru"
    title = "Полная история версий" if ru else "Full version history"
    intro = (
        "Все версии проекта «Вкус Ближнего Востока». Текущая версия — v2.1.1."
        if ru
        else "All versions of Taste of the Middle East. Current version: v2.1.1."
    )
    doc = SimpleDocTemplate(
        str(ROOT / out_name),
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
    )
    styles = {
        "kicker": ParagraphStyle("kicker", fontName="Arial-Bold", fontSize=8, leading=10, textColor=MUTED, spaceAfter=4),
        "title": ParagraphStyle("title", fontName="Arial-Bold", fontSize=30, leading=34, textColor=INK, spaceAfter=10),
        "lead": ParagraphStyle("lead", fontName="Arial", fontSize=10.5, leading=15, textColor=MUTED, spaceAfter=18),
        "version": ParagraphStyle("version", fontName="Arial-Bold", fontSize=16, leading=20, textColor=INK, spaceAfter=2),
        "date": ParagraphStyle("date", fontName="Arial", fontSize=8, leading=11, textColor=MUTED, spaceAfter=8),
        "item": ParagraphStyle("item", fontName="Arial", fontSize=9.4, leading=13, textColor=INK),
        "footer": ParagraphStyle("footer", fontName="Arial", fontSize=7.5, leading=10, textColor=MUTED),
    }
    story = [
        Paragraph("ВКУС БЛИЖНЕГО ВОСТОКА" if ru else "VKUS BLIZHNEGO VOSTOKA", styles["kicker"]),
        Paragraph(title, styles["title"]),
        Paragraph(intro, styles["lead"]),
    ]
    for version, date, changes in HISTORY:
        story.append(Paragraph(f"v{version}", styles["version"]))
        story.append(Paragraph(date, styles["date"]))
        story.append(
            ListFlowable(
                [ListItem(Paragraph(item, styles["item"]), leftIndent=12) for item in changes[lang]],
                bulletType="bullet",
                start="•",
                leftIndent=12,
            )
        )
        story.append(Spacer(1, 8 * mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=8 * mm))
    story.append(
        Paragraph(
            "© 2026 · Вкус Ближнего Востока · v2.1.1" if ru else "© 2026 · Vkus Blizhnego Vostoka · v2.1.1",
            styles["footer"],
        )
    )
    doc.build(story)


if __name__ == "__main__":
    build("ru", "history-full.pdf")
    build("en", "history-full-en.pdf")
    print("history PDFs built")
