# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from recipes_data import RECIPES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PHOTO_SOURCES = {
    "koshary": "https://commons.wikimedia.org/wiki/File:Egyptian_food_Koshary.jpg",
    "hawawshi": "https://commons.wikimedia.org/wiki/File:Egyptian_meatloaf.jpg",
    "goulash": "https://commons.wikimedia.org/wiki/File:Meat_burek_(GAK_bakery,_Belgrade,_Serbia).jpg",
    "macaroni": "https://commons.wikimedia.org/wiki/File:Macarona_bechamel.jpg",
    "fattah": "https://commons.wikimedia.org/wiki/File:Fattah_at_Felfela_Restaurant_-_Cairo_Egypt_October_2009.jpg",
    "molokheya": "https://commons.wikimedia.org/wiki/File:Molokheya_and_rice_with_chiken,_Egypt_2012.JPG",
    "mesaka": "https://commons.wikimedia.org/wiki/File:Patl%C4%B1can_dish.jpg",
    "mahshi": "https://commons.wikimedia.org/wiki/File:Libyan_Mahshi_%D8%A3%D9%83%D9%84%D8%A9_%D8%A7%D9%84%D9%85%D8%AD%D8%B4%D9%8A_%D8%A7%D9%84%D9%8A%D8%A8%D9%8A%D8%A9.JPG",
    "ful": "https://commons.wikimedia.org/wiki/File:Ful_Medames.JPG",
    "kofta": "https://commons.wikimedia.org/wiki/File:Kafta_shish_kebab_and_grilled_vegetables_on_salad_-_Cambridge,_MA.jpg",
}


def build_data():
    data = []
    for recipe in RECIPES:
        item = dict(recipe)
        item["pdfPath"] = f"pdfs/{recipe['num']}_{recipe['id']}.pdf"
        item["photoSource"] = PHOTO_SOURCES.get(recipe["id"], "")
        data.append(item)
    return data


if __name__ == "__main__":
    text = "window.RECIPES = " + json.dumps(build_data(), ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "data.js").write_text(text, encoding="utf-8")
    print("data.js written:", len(text), "characters")
