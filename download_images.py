import urllib.request
import ssl
import time
import duckdb
import os

os.makedirs("images/champions", exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE

NAME_MAP = {
    '아트록스': 'Aatrox', '브라이어': 'Briar', '케이틀린': 'Caitlyn',
    '초가스': 'Cho%27Gath', '이즈리얼': 'Ezreal', '레오나': 'Leona',
    '리산드라': 'Lissandra', '나서스': 'Nasus', '뽀삐': 'Poppy',
    '렉사이': 'RekSai', '탈론': 'Talon', '티모': 'Teemo',
    '트위스티드 페이트': 'TwistedFate', '베이가': 'Veigar',
    '아칼리': 'Akali', '벨베스': 'Belveth', '나르': 'Gnar',
    '그라가스': 'Gragas', '그웬': 'Gwen', '잭스': 'Jax',
    '징크스': 'Jinx', '밀리오': 'Milio', '모데카이저': 'Mordekaiser',
    '판테온': 'Pantheon', '파이크': 'Pyke', '조이': 'Zoe',
    '오로라': 'Aurora', '다이아나': 'Diana', '피즈': 'Fizz',
    '일라오이': 'Illaoi', '카이사': 'Kaisa', '룰루': 'Lulu',
    '마오카이': 'Maokai', '미스 포츈': 'MissFortune', '오른': 'Ornn',
    '레스트': 'Kayn', '사미라': 'Samira', '우르곳': 'Urgot',
    '빅토르': 'Viktor', '아우렐리온 솔': 'AurelionSol', '코르키': 'Corki',
    '카르마': 'Karma', '킨드레드': 'Kindred', '르블랑': 'Leblanc',
    '마스터 이': 'MasterYi', '나미': 'Nami', '누누': 'NunuWillump',
    '람머스': 'Rammus', '리븐': 'Riven', '탐 켄치': 'TahmKench',
    '자야': 'Xayah', '바드': 'Bard', '블리츠크랭크': 'Blitzcrank',
    '피오라': 'Fiora', '그레이브즈': 'Graves', '진': 'Jhin',
    '모르가나': 'Morgana', '쉔': 'Shen', '소나': 'Sona',
    '벡스': 'Vex', '제드': 'Zed',
    '밉시': 'Teemo', '마이티 메카': 'Urgot',
}

VERSION = "15.10.1"
BASE    = f"https://ddragon.leagueoflegends.com/cdn/{VERSION}/img/champion"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}

con = duckdb.connect("tft_gold.duckdb")
champs = con.execute("SELECT id, name FROM champion").fetchall()

ok, fail = 0, 0
for cid, name in champs:
    eng = NAME_MAP.get(name)
    if not eng:
        print(f"  ⚠️  매핑 없음: {name}")
        continue
    path = f"images/champions/{eng.lower()}.png"
    url  = f"{BASE}/{eng}.png"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx) as r:
            with open(path, 'wb') as f:
                f.write(r.read())
        con.execute("UPDATE champion SET image_path=? WHERE id=?", [path, cid])
        print(f"  ✅ {name}")
        ok += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        fail += 1
    time.sleep(0.1)

con.close()
print(f"\n완료: 성공 {ok}개 / 실패 {fail}개")
