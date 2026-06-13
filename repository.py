import sys
sys.stdout.reconfigure(encoding='utf-8')

from database import get_connection


class ChampionRepository:

    def find_all(self, cost: int = 0) -> list[dict]:
        con = get_connection()
        if cost == 0:
            rows = con.execute(
                "SELECT * FROM champion ORDER BY cost, name"
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM champion WHERE cost = ? ORDER BY name", [cost]
            ).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","name","cost","hp","atk","image_path"]) for r in rows]

    def find_by_id(self, id: int) -> dict | None:
        con = get_connection()
        row = con.execute("SELECT * FROM champion WHERE id = ?", [id]).fetchone()
        con.close()
        return _row_to_dict(row, ["id","name","cost","hp","atk","image_path"]) if row else None

    def find_by_keyword(self, keyword: str) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM champion WHERE name LIKE ? ORDER BY cost, name",
            [f"%{keyword}%"]
        ).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","name","cost","hp","atk","image_path"]) for r in rows]


class TraitRepository:

    def find_all(self) -> list[dict]:
        con = get_connection()
        rows = con.execute("SELECT * FROM trait ORDER BY name").fetchall()
        con.close()
        return [_row_to_dict(r, ["id","name","trait_type","description","thresholds","image_path"]) for r in rows]

    def find_by_id(self, id: int) -> dict | None:
        con = get_connection()
        row = con.execute("SELECT * FROM trait WHERE id = ?", [id]).fetchone()
        con.close()
        return _row_to_dict(row, ["id","name","trait_type","description","thresholds","image_path"]) if row else None

    def find_by_keyword(self, keyword: str) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM trait WHERE name LIKE ? ORDER BY name", [f"%{keyword}%"]
        ).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","name","trait_type","description","thresholds","image_path"]) for r in rows]


class ItemRepository:

    def find_all(self) -> list[dict]:
        con = get_connection()
        rows = con.execute("SELECT * FROM item ORDER BY stat_type, name").fetchall()
        con.close()
        return [_row_to_dict(r, ["id","name","stat_type","gp","image_path"]) for r in rows]

    def find_by_id(self, id: int) -> dict | None:
        con = get_connection()
        row = con.execute("SELECT * FROM item WHERE id = ?", [id]).fetchone()
        con.close()
        return _row_to_dict(row, ["id","name","stat_type","gp","image_path"]) if row else None

class DeckRepository:

    def find_all(self) -> list[dict]:
        con = get_connection()
        rows = con.execute("SELECT * FROM deck ORDER BY total_cost").fetchall()
        con.close()
        return [_to_deck(r) for r in rows]

    def find_by_id(self, id: int) -> dict | None:
        con = get_connection()
        row = con.execute("SELECT * FROM deck WHERE id = ?", [id]).fetchone()
        con.close()
        return _to_deck(row) if row else None

    def find_by_gold(self, gold: int) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM deck WHERE total_cost <= ? ORDER BY total_cost",
            [gold]
        ).fetchall()
        con.close()
        return [_to_deck(r) for r in rows]

    def find_by_gold_and_difficulty(self, gold: int, tier: str) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM deck WHERE total_cost <= ? AND tier = ? ORDER BY total_cost",
            [gold, tier]
        ).fetchall()
        con.close()
        return [_to_deck(r) for r in rows]

    def save(self, data: dict) -> int:
        con = get_connection()
        max_id = con.execute("SELECT COALESCE(MAX(id),0)+1 FROM deck").fetchone()[0]
        con.execute(
            "INSERT INTO deck VALUES (?,?,?,?,?,?,?)",
            [max_id, data["name"], data["total_cost"], data.get("tier","B"),
             data.get("playstyle",""), data.get("patch_version","17.3b"), data.get("memo","")]
        )
        con.close()
        return max_id

    def delete_by_id(self, id: int):
        con = get_connection()
        con.execute("DELETE FROM recommend_item WHERE deck_unit_id IN (SELECT id FROM deck_unit WHERE deck_id=?)", [id])
        con.execute("DELETE FROM deck_unit    WHERE deck_id = ?",   [id])
        con.execute("DELETE FROM deck_synergy WHERE deck_id = ?",   [id])
        con.execute("DELETE FROM deck          WHERE id = ?",       [id])
        con.close()

class DeckUnitRepository:

    def find_by_deck_id(self, deck_id: int) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM deck_unit WHERE deck_id = ? ORDER BY is_carry DESC, star_level DESC",
            [deck_id]
        ).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","deck_id","champion_id","is_carry","star_level"]) for r in rows]

    def save_all(self, deck_id: int, units: list[dict]):
        con = get_connection()
        max_id = con.execute("SELECT COALESCE(MAX(id),0) FROM deck_unit").fetchone()[0]
        for i, u in enumerate(units, 1):
            con.execute(
                "INSERT OR IGNORE INTO deck_unit VALUES (?,?,?,?,?)",
                [max_id+i, deck_id, u["champion_id"], u.get("is_carry",False), u.get("star_level",1)]
            )
        con.close()

    def delete_by_deck_id(self, deck_id: int):
        con = get_connection()
        con.execute("DELETE FROM deck_unit WHERE deck_id = ?", [deck_id])
        con.close()

class DeckSynergyRepository:

    def find_by_deck_id(self, deck_id: int) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM deck_synergy WHERE deck_id = ? ORDER BY active_count DESC",
            [deck_id]
        ).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","deck_id","trait_id","active_count"]) for r in rows]

    def save_all(self, deck_id: int, synergies: list[dict]):
        con = get_connection()
        max_id = con.execute("SELECT COALESCE(MAX(id),0) FROM deck_synergy").fetchone()[0]
        for i, s in enumerate(synergies, 1):
            con.execute(
                "INSERT OR IGNORE INTO deck_synergy VALUES (?,?,?,?)",
                [max_id+i, deck_id, s["trait_id"], s.get("active_count",2)]
            )
        con.close()

    def delete_by_deck_id(self, deck_id: int):
        con = get_connection()
        con.execute("DELETE FROM deck_synergy WHERE deck_id = ?", [deck_id])
        con.close()

class RecommendItemRepository:

    def find_by_deck_unit_id(self, deck_unit_id: int) -> list[dict]:
        con = get_connection()
        rows = con.execute(
            "SELECT * FROM recommend_item WHERE deck_unit_id = ? ORDER BY priority",
            [deck_unit_id]
        ).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","deck_unit_id","item_id","priority"]) for r in rows]

    def save_all(self, deck_unit_id: int, items: list[dict]):
        con = get_connection()
        max_id = con.execute("SELECT COALESCE(MAX(id),0) FROM recommend_item").fetchone()[0]
        for i, item in enumerate(items, 1):
            con.execute(
                "INSERT OR IGNORE INTO recommend_item VALUES (?,?,?,?)",
                [max_id+i, deck_unit_id, item["item_id"], i]
            )
        con.close()

class JoinRepository:

    def find_deck_with_champions_by_gold(self, gold: int) -> list[dict]:
        """★ 핵심: deck LEFT JOIN deck_unit LEFT JOIN champion"""
        con = get_connection()
        rows = con.execute("""
            SELECT
                d.id            AS deck_id,
                d.name          AS deck_name,
                d.total_cost,
                d.tier,
                d.playstyle,
                d.patch_version,
                d.memo,
                ch.id           AS champion_id,
                ch.name         AS champion_name,
                ch.cost         AS champion_cost,
                ch.image_path   AS champion_img,
                du.is_carry,
                du.star_level,
                du.id           AS deck_unit_id
            FROM deck d
            LEFT JOIN deck_unit du ON d.id = du.deck_id
            LEFT JOIN champion  ch ON du.champion_id = ch.id
            WHERE d.total_cost <= ?
            ORDER BY d.total_cost ASC, du.is_carry DESC
        """, [gold]).fetchall()
        con.close()
        cols = ["deck_id","deck_name","total_cost","tier","playstyle",
                "patch_version","memo","champion_id","champion_name",
                "champion_cost","champion_img","is_carry","star_level","deck_unit_id"]
        return [_row_to_dict(r, cols) for r in rows]

    def find_deck_with_traits(self, deck_id: int) -> list[dict]:
        """deck LEFT JOIN deck_synergy LEFT JOIN trait"""
        con = get_connection()
        rows = con.execute("""
            SELECT
                t.id            AS trait_id,
                t.name          AS trait_name,
                t.trait_type,
                t.thresholds,
                t.image_path    AS trait_img,
                ds.active_count
            FROM deck_synergy ds
            LEFT JOIN trait t ON ds.trait_id = t.id
            WHERE ds.deck_id = ?
            ORDER BY ds.active_count DESC
        """, [deck_id]).fetchall()
        con.close()
        cols = ["trait_id","trait_name","trait_type","thresholds","trait_img","active_count"]
        return [_row_to_dict(r, cols) for r in rows]

    def find_units_with_items(self, deck_id: int) -> list[dict]:
        """deck_unit LEFT JOIN recommend_item LEFT JOIN item"""
        con = get_connection()
        rows = con.execute("""
            SELECT
                du.id           AS deck_unit_id,
                ch.name         AS champion_name,
                du.is_carry,
                i.name          AS item_name,
                i.stat_type,
                i.image_path    AS item_img,
                ri.priority
            FROM deck_unit du
            LEFT JOIN champion       ch ON du.champion_id  = ch.id
            LEFT JOIN recommend_item ri ON du.id            = ri.deck_unit_id
            LEFT JOIN item           i  ON ri.item_id       = i.id
            WHERE du.deck_id = ?
            ORDER BY du.is_carry DESC, ri.priority
        """, [deck_id]).fetchall()
        con.close()
        cols = ["deck_unit_id","champion_name","is_carry",
                "item_name","stat_type","item_img","priority"]
        return [_row_to_dict(r, cols) for r in rows]

    def find_champions_by_trait(self, trait_id: int) -> list[dict]:
        """trait 관련 챔피언 조회"""
        con = get_connection()
        rows = con.execute("""
            SELECT DISTINCT ch.id, ch.name, ch.cost, ch.image_path
            FROM deck_synergy ds
            LEFT JOIN deck_unit du ON ds.deck_id = du.deck_id
            LEFT JOIN champion  ch ON du.champion_id = ch.id
            WHERE ds.trait_id = ?
            ORDER BY ch.cost, ch.name
        """, [trait_id]).fetchall()
        con.close()
        return [_row_to_dict(r, ["id","name","cost","image_path"]) for r in rows]

def _row_to_dict(row, cols: list[str]) -> dict:
    return dict(zip(cols, row))

def _to_deck(row) -> dict:
    return _row_to_dict(row, ["id","name","total_cost","tier","playstyle","patch_version","memo"])