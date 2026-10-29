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
    "hummus": "https://commons.wikimedia.org/wiki/File:Hummus_plate.jpg",
    "tabbouleh": "https://commons.wikimedia.org/wiki/File:Tabouleh_1.JPG",
    "muhammara": "https://commons.wikimedia.org/wiki/File:Antakya_usul%C3%BC_Muhammara.jpg",
    "shawarma": "https://commons.wikimedia.org/wiki/File:Shawarma-sandwich-01.jpg",
    "menemen": "https://commons.wikimedia.org/wiki/File:Menemen_in_pan.jpg",
    "lahmacun": "https://commons.wikimedia.org/wiki/File:Lahmacun.jpg",
    "shakshuka": "https://commons.wikimedia.org/wiki/File:Shakshuka1.jpg",
    "sabich": "https://commons.wikimedia.org/wiki/File:Sabich.jpg",
    "baba-ghanoush": "https://commons.wikimedia.org/wiki/File:Baba_Ghanoush.jpg",
    "falafel": "https://commons.wikimedia.org/wiki/File:Dishes_at_falafel_shop_in_Roppongi.jpg",
    "fattoush": "https://commons.wikimedia.org/wiki/File:Arabic_Fattoush_Salad_(24934823760).png",
    "manakish": "https://commons.wikimedia.org/wiki/File:Israeli_zaatar_manakeesh.jpg",
    "shish-taouk": "https://commons.wikimedia.org/wiki/File:A_dish_of_Shish_taouk.jpg",
    "batata-harra": "https://commons.wikimedia.org/wiki/File:Batata_harra.jpg",
    "kibbeh": "https://commons.wikimedia.org/wiki/File:Fried_lamb_kibbeh_1.JPG",
    "kafta": "https://commons.wikimedia.org/wiki/File:Kafta_Serving.JPG",
    "yabraq": "https://commons.wikimedia.org/wiki/File:Crimean_Tatar_sarma_Stage_6.jpg",
    "shakriyeh": "https://commons.wikimedia.org/wiki/File:MyPlate_gov_Cultural_Food_(20241025-USDA-FNS-UNK-0046).jpg",
    "freekeh-soup": "https://commons.wikimedia.org/wiki/File:Chorba_Frik.jpg",
    "sfiha": "https://commons.wikimedia.org/wiki/File:Brazilian_sfiha.jpg",
    "fattet-hummus": "https://commons.wikimedia.org/wiki/File:Fatethomos.JPG",
    "kebab-halabi": "https://commons.wikimedia.org/wiki/File:Halep_isi_kebap.jpg",
    "maamoul": "https://commons.wikimedia.org/wiki/File:Ma%27amoul_Filled_with_Dates_and_Nuts.jpg",
    "halawet-el-jibn": "https://commons.wikimedia.org/wiki/File:Halawet_el-Jibn_served_in_Jerusalem,_Israel.jpg",
    "mercimek": "https://commons.wikimedia.org/wiki/File:Lentil_soup_boiling.jpg",
    "kofte": "https://commons.wikimedia.org/wiki/File:Kofte-pilav.jpg",
    "imam-bayildi": "https://commons.wikimedia.org/wiki/File:Crimean_Tatar_Imam_bayildi.jpg",
    "karniyarik": "https://commons.wikimedia.org/wiki/File:KARNIYARIK_in_Ankara.jpg",
    "gozleme": "https://commons.wikimedia.org/wiki/File:G%C3%B6zleme.JPG",
    "kisir": "https://commons.wikimedia.org/wiki/File:2016-02-07_Bulgursalat_anagoria.JPG",
    "tavuk-sis": "https://commons.wikimedia.org/wiki/File:Tavuk_%C5%9Ei%C5%9F.jpg",
    "baklava": "https://commons.wikimedia.org/wiki/File:2018-04-28_Turkish_baklava_in_Australian_turkish_cafe.jpg",
    "musakhan": "https://commons.wikimedia.org/wiki/File:Mussakhan-2.jpg",
    "maqluba": "https://commons.wikimedia.org/wiki/File:Makluba.JPG",
    "maftoul": "https://commons.wikimedia.org/wiki/File:Couscous-1.jpg",
    "shishbarak": "https://commons.wikimedia.org/wiki/File:Dushbara_Azerbaijani_cuisine.jpg",
    "knafeh": "https://commons.wikimedia.org/wiki/File:2019_Marin_Greek_Festival_-_Sarah_Stierch_05.jpg",
    "qidra": "https://commons.wikimedia.org/wiki/File:Jerusalem_Qidreh_at_Amigo_Emil_(6035879431).jpg",
    "bamia": "https://commons.wikimedia.org/wiki/File:Bamia-Ocras_tomate.JPG",
    "mujaddara": "https://commons.wikimedia.org/wiki/File:Liat_Portal_for_Foodie_Disorder_-_Mujaddara.jpg",
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
