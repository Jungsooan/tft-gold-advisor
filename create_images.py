from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("images/champions", exist_ok=True)
os.makedirs("images/traits",   exist_ok=True)
os.makedirs("images/items",    exist_ok=True)

COST_COLOR = {
    1: (150, 150, 150),
    2: (34,  197, 94),
    3: (59,  130, 246),
    4: (168, 85,  247),
    5: (234, 179, 8),
}

TRAIT_COLOR = {
    "계열": (59, 130, 246),
    "직업": (34, 197, 94),
}

ITEM_COLOR = {
    "공격력": (239, 68,  68),
    "방어력": (59,  130, 246),
    "마법":   (168, 85,  247),
    "유틸":   (34,  197, 94),
}

def make_champion_img(name, cost, path):
    img  = Image.new("RGB", (80, 80), color=COST_COLOR.get(cost, (100,100,100)))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2,2,77,77], outline=(255,255,255), width=2)
    short = name[:3]
    draw.text((40,32), short, fill=(255,255,255), anchor="mm")
    draw.text((40,62), f"{cost}G",  fill=(255,255,200), anchor="mm")
    img.save(path)

def make_trait_img(name, trait_type, path):
    clr  = TRAIT_COLOR.get(trait_type, (100,100,100))
    img  = Image.new("RGB", (60, 60), color=clr)
    draw = ImageDraw.Draw(img)
    draw.ellipse([3,3,56,56], outline=(255,255,255), width=2)
    draw.text((30,30), name[:2], fill=(255,255,255), anchor="mm")
    img.save(path)

def make_item_img(name, stat_type, path):
    clr  = ITEM_COLOR.get(stat_type, (100,100,100))
    img  = Image.new("RGB", (60, 60), color=clr)
    draw = ImageDraw.Draw(img)
    draw.rectangle([4,4,55,55], outline=(255,215,0), width=2)
    draw.text((30,30), name[:2], fill=(255,255,255), anchor="mm")
    img.save(path)

import duckdb
con = duckdb.connect("tft_gold.duckdb")

print("챔피언 이미지 생성 중...")
champs = con.execute("SELECT name, cost, image_path FROM champion").fetchall()
for name, cost, path in champs:
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        make_champion_img(name, cost, path)
print(f"  {len(champs)}개 생성 완료")

print("특성 이미지 생성 중...")
traits = con.execute("SELECT name, trait_type, image_path FROM trait").fetchall()
for name, ttype, path in traits:
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        make_trait_img(name, ttype or "계열", path)
print(f"  {len(traits)}개 생성 완료")

print("아이템 이미지 생성 중...")
items = con.execute("SELECT name, stat_type, image_path FROM item").fetchall()
for name, stype, path in items:
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        make_item_img(name, stype or "공격력", path)
print(f"  {len(items)}개 생성 완료")

con.close()
print("\n모든 이미지 생성 완료!")
print("images/ 폴더를 확인하세요.")
