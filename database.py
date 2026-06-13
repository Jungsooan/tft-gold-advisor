import duckdb
import os

DB_PATH = "tft_gold.duckdb"


def get_connection():
    return duckdb.connect(DB_PATH)


def init_db():
    con = get_connection()



    con.execute("""
        CREATE TABLE IF NOT EXISTS champion (
            id         INTEGER PRIMARY KEY,
            name       VARCHAR(50) NOT NULL,
            cost       TINYINT     NOT NULL,
            hp         SMALLINT,
            atk        SMALLINT,
            image_path VARCHAR(200)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS trait (
            id          INTEGER PRIMARY KEY,
            name        VARCHAR(50) NOT NULL,
            trait_type  VARCHAR(20),
            description TEXT,
            thresholds  VARCHAR(30),
            image_path  VARCHAR(200)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS item (
            id         INTEGER PRIMARY KEY,
            name       VARCHAR(60) NOT NULL,
            stat_type  VARCHAR(20),
            gp         SMALLINT,
            image_path VARCHAR(200)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS deck (
            id            INTEGER PRIMARY KEY,
            name          VARCHAR(80) NOT NULL,
            total_cost    SMALLINT    NOT NULL,
            tier          CHAR(1),
            playstyle     VARCHAR(40),
            patch_version VARCHAR(10),
            memo          TEXT
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS deck_unit (
            id           INTEGER PRIMARY KEY,
            deck_id      INTEGER NOT NULL,
            champion_id  INTEGER NOT NULL,
            is_carry     BOOLEAN DEFAULT false,
            star_level   TINYINT DEFAULT 1,
            UNIQUE (deck_id, champion_id),
            FOREIGN KEY (deck_id)     REFERENCES deck(id),
            FOREIGN KEY (champion_id) REFERENCES champion(id)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS deck_synergy (
            id           INTEGER PRIMARY KEY,
            deck_id      INTEGER NOT NULL,
            trait_id     INTEGER NOT NULL,
            active_count TINYINT,
            UNIQUE (deck_id, trait_id),
            FOREIGN KEY (deck_id)  REFERENCES deck(id),
            FOREIGN KEY (trait_id) REFERENCES trait(id)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS recommend_item (
            id           INTEGER PRIMARY KEY,
            deck_unit_id INTEGER NOT NULL,
            item_id      INTEGER NOT NULL,
            priority     TINYINT,
            UNIQUE (deck_unit_id, item_id),
            FOREIGN KEY (deck_unit_id) REFERENCES deck_unit(id),
            FOREIGN KEY (item_id)      REFERENCES item(id)
        )
    """)

    

    if con.execute("SELECT COUNT(*) FROM champion").fetchone()[0] > 0:
        print("이미 데이터가 존재합니다.")
        con.close()
        return

  
    con.executemany("INSERT INTO champion VALUES (?,?,?,?,?,?)", [
        (1,  "코그모",       1,  550,  40, "images/champions/cogmaw.png"),
        (2,  "말파이트",     1,  600,  45, "images/champions/malphite.png"),
        (3,  "틸트워커",     1,  500,  50, "images/champions/tiltwatcher.png"),
        (4,  "람머스",       2,  700,  55, "images/champions/rammus.png"),
        (5,  "징크스",       2,  600,  60, "images/champions/jinx.png"),
        (6,  "카직스",       2,  620,  65, "images/champions/khazix.png"),
        (7,  "럼블",         3,  750,  70, "images/champions/rumble.png"),
        (8,  "야스오",       3,  800,  75, "images/champions/yasuo.png"),
        (9,  "모르가나",     3,  700,  60, "images/champions/morgana.png"),
        (10, "아무무",       4,  900,  80, "images/champions/amumu.png"),
        (11, "소라카",       4,  750,  55, "images/champions/soraka.png"),
        (12, "그레이브즈",   4,  850,  85, "images/champions/graves.png"),
        (13, "아우렐리온솔", 5, 1000,  90, "images/champions/aurelionsol.png"),
        (14, "쓰레쉬",       5,  950,  70, "images/champions/thresh.png"),
    ])

    con.executemany("INSERT INTO trait VALUES (?,?,?,?,?,?)", [
        (1, "태고족",     "공격형", "군체 유충 소환, 전투 후 챔피언 획득",        "3/5/7",   "images/traits/ancient.png"),
        (2, "시간균열자", "지원형", "패배 시 무료 새로고침, 승리 시 경험치 획득", "2/4/6",   "images/traits/timerift.png"),
        (3, "암흑의 별",  "공격형", "블랙홀 생성, 대질량 상태 부여",             "3/5/7",   "images/traits/darkstar.png"),
        (4, "동물특공대", "공격형", "무기 획득 및 강화, 사망 시 무기 전수",       "3/5/7/9", "images/traits/animal.png"),
        (5, "우주 그루브","지원형", "특성 하나당 공격속도·방어력·마저 증가",      "3/5/7",   "images/traits/groove.png"),
        (6, "별돌보미",   "지원형", "별자리에 따라 다른 효과 적용 (7가지)",       "2/4/6",   "images/traits/starguard.png"),
        (7, "중재자",     "지원형", "전투 전 보호막 및 공격속도 부여",            "2/4",     "images/traits/arbiter.png"),
        (8, "정령족",     "지원형", "전투 시작 시 유물 소환",                     "2/4/6",   "images/traits/spirit.png"),
    ])

   
    con.executemany("INSERT INTO item VALUES (?,?,?,?,?)", [
        (1, "용사의 손길",   "공격력", 500, "images/items/hero_hand.png"),
        (2, "방어의 용기",   "방어력", 400, "images/items/shield.png"),
        (3, "마법의 힘",     "마법",   450, "images/items/magic.png"),
        (4, "회복의 빛",     "유틸",   350, "images/items/heal.png"),
        (5, "치명적 날개",   "공격력", 550, "images/items/wing.png"),
        (6, "강철 방어구",   "방어력", 420, "images/items/steel.png"),
        (7, "속도의 구슬",   "유틸",   380, "images/items/speed.png"),
        (8, "폭풍의 검",     "공격력", 600, "images/items/storm.png"),
    ])

    con.executemany("INSERT INTO deck VALUES (?,?,?,?,?,?,?)", [
        (1, "태고족 속공 덱",    12, "B", "속전속결",   "17.3b", "초반 태고족으로 빠른 스노우볼링"),
        (2, "시간균열자 리롤 덱",18, "A", "패배 후 역전","17.3b", "패패 전략으로 리소스 축적"),
        (3, "암흑의별 야스오 덱",22, "A", "중반 안정",  "17.3b", "야스오 캐리 + 블랙홀 제어"),
        (4, "소라카 힐링 덱",    28, "S", "후반 역전",  "17.3b", "소라카 중심 후반 생존 전략"),
        (5, "아우렐리온솔 덱",   38, "S", "후반 역전",  "17.3b", "5코스트 풀코스트 하드캐리"),
    ])

   
    con.executemany("INSERT INTO deck_unit VALUES (?,?,?,?,?)", [

        (1,  1, 1, False, 2), (2,  1, 2, False, 1),
        (3,  1, 4, True,  2), (4,  1, 7, False, 1),
        (5,  2, 3, False, 1), (6,  2, 5, True,  3),
        (7,  2, 6, False, 2), (8,  2, 10,False, 1),
        (9,  3, 8, True,  2), (10, 3, 9, False, 1),
        (11, 3, 6, False, 2), (12, 3, 10,False, 1),
        (13, 4, 11,True,  2), (14, 4, 9, False, 1),
        (15, 4, 2, False, 1), (16, 4, 12,False, 1),
        (17, 5, 13,True,  2), (18, 5, 11,False, 1),
        (19, 5, 12,False, 1), (20, 5, 9, False, 1),
    ])

    con.executemany("INSERT INTO deck_synergy VALUES (?,?,?,?)", [
        (1,  1, 1, 3), (2,  1, 2, 2),
        (3,  2, 2, 4), (4,  2, 1, 3),
        (5,  3, 3, 3), (6,  3, 4, 3),
        (7,  4, 6, 4), (8,  4, 5, 3),
        (9,  5, 5, 3), (10, 5, 7, 2),
    ])

    
    con.executemany("INSERT INTO recommend_item VALUES (?,?,?,?)", [
        (1, 3,  1, 1), (2, 3,  5, 2), (3, 3,  8, 3),  
        (4, 6,  1, 1), (5, 6,  5, 2),                  
        (6, 9,  8, 1), (7, 9,  1, 2), (8, 9,  5, 3),  
        (9, 13, 4, 1), (10,13, 3, 2),                  
        (11,17, 8, 1), (12,17, 1, 2), (13,17, 5, 3),  
    ])

    con.close()
    print(" DB 초기화 완료")
    print("   - champion : 14건")
    print("   - trait    :  8건")
    print("   - item     :  8건")
    print("   - deck     :  5건")
    print("   - deck_unit: 20건")
    print("   - deck_synergy: 10건")
    print("   - recommend_item: 13건")


if __name__ == "__main__":
    init_db()

    con = get_connection()
    print("\n 테이블 목록:")
    tables = con.execute("SHOW TABLES").fetchall()
    for t in tables:
        cnt = con.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
        print(f"   {t[0]:<20} {cnt}건")

    print("\n🔗 3-Table LEFT JOIN 테스트:")
    rows = con.execute("""
        SELECT
            d.name          AS deck_name,
            d.total_cost,
            ch.name         AS champion_name,
            ch.cost         AS champion_cost,
            du.is_carry
        FROM deck d
        LEFT JOIN deck_unit du ON d.id = du.deck_id
        LEFT JOIN champion  ch ON du.champion_id = ch.id
        WHERE d.total_cost <= 20
        ORDER BY d.total_cost, du.is_carry DESC
    """).fetchall()
    for r in rows:
        carry = "★캐리" if r[4] else "     "
        print(f"   [{r[1]}G] {r[0]:<20} | {carry} {r[2]}({r[3]}코)")
    con.close()
