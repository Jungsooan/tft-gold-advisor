from repository import (
    ChampionRepository, TraitRepository, ItemRepository,
    DeckRepository, DeckUnitRepository, DeckSynergyRepository,
    RecommendItemRepository, JoinRepository
)
from collections import defaultdict

_champion_repo      = ChampionRepository()
_trait_repo         = TraitRepository()
_item_repo          = ItemRepository()
_deck_repo          = DeckRepository()
_deck_unit_repo     = DeckUnitRepository()
_deck_synergy_repo  = DeckSynergyRepository()
_rec_item_repo      = RecommendItemRepository()
_join_repo          = JoinRepository()


# ── 4.1 골드 기반 덱 추천 ─────────────────────────────

def get_decks_by_gold(gold: int, tier: str = "전체") -> list[dict]:
    """
    gold 이하 total_cost 덱 + 챔피언 정보를 그룹핑해서 반환.
    반환 형태:
    [
      {
        deck_id, deck_name, total_cost, tier, playstyle, patch_version, memo,
        champions: [ {champion_name, champion_cost, is_carry, star_level, ...} ],
        traits:    [ {trait_name, thresholds, active_count} ]
      }, ...
    ]
    """
    if tier and tier != "전체":
        raw = _deck_repo.find_by_gold_and_difficulty(gold, tier)
        # JOIN은 골드 조건으로 먼저 받아서 tier 필터
        all_rows = _join_repo.find_deck_with_champions_by_gold(gold)
        all_rows = [r for r in all_rows if r["tier"] == tier]
    else:
        all_rows = _join_repo.find_deck_with_champions_by_gold(gold)

    # deck_id 기준으로 그룹핑
    decks: dict[int, dict] = {}
    for r in all_rows:
        did = r["deck_id"]
        if did not in decks:
            decks[did] = {
                "deck_id":      did,
                "deck_name":    r["deck_name"],
                "total_cost":   r["total_cost"],
                "tier":         r["tier"],
                "playstyle":    r["playstyle"],
                "patch_version":r["patch_version"],
                "memo":         r["memo"],
                "champions":    [],
                "traits":       [],
            }
        if r["champion_name"]:
            decks[did]["champions"].append({
                "champion_id":   r["champion_id"],
                "champion_name": r["champion_name"],
                "champion_cost": r["champion_cost"],
                "champion_img":  r["champion_img"],
                "is_carry":      r["is_carry"],
                "star_level":    r["star_level"],
                "deck_unit_id":  r["deck_unit_id"],
            })

    # 특성 정보 추가
    for did, deck in decks.items():
        deck["traits"] = _join_repo.find_deck_with_traits(did)

    return list(decks.values())


# ── 4.2 덱 상세 조회 ──────────────────────────────────

def get_deck_detail(deck_id: int) -> dict | None:
    deck = _deck_repo.find_by_id(deck_id)
    if not deck:
        return None
    deck["champions"] = []
    units = _deck_unit_repo.find_by_deck_id(deck_id)
    for u in units:
        ch = _champion_repo.find_by_id(u["champion_id"])
        if ch:
            ch["is_carry"]    = u["is_carry"]
            ch["star_level"]  = u["star_level"]
            ch["deck_unit_id"]= u["id"]
            deck["champions"].append(ch)
    deck["traits"] = _join_repo.find_deck_with_traits(deck_id)
    deck["items"]  = _join_repo.find_units_with_items(deck_id)
    return deck


# ── 4.3 챔피언 탭 조회 ────────────────────────────────

def get_all_champions(cost: int = 0) -> list[dict]:
    return _champion_repo.find_all(cost)

def search_champions(keyword: str) -> list[dict]:
    return _champion_repo.find_by_keyword(keyword)


# ── 4.4 특성 탭 조회 ──────────────────────────────────

def get_all_traits() -> list[dict]:
    return _trait_repo.find_all()

def get_champions_by_trait(trait_id: int) -> list[dict]:
    return _join_repo.find_champions_by_trait(trait_id)


# ── 4.5 덱 등록 ───────────────────────────────────────

def save_deck(
    deck_data: dict,
    champion_ids: list[int],
    carry_id: int,
    trait_ids: list[int],
    item_ids: list[int] = []
) -> int:
    """덱 + 유닛 + 시너지 + 추천 아이템을 한 번에 저장"""

    # total_cost 자동 계산 (입력 없을 시)
    if not deck_data.get("total_cost"):
        champs = [_champion_repo.find_by_id(cid) for cid in champion_ids]
        deck_data["total_cost"] = sum(c["cost"] for c in champs if c)

    deck_id = _deck_repo.save(deck_data)

    # deck_unit 저장
    units = [
        {"champion_id": cid, "is_carry": cid == carry_id, "star_level": 1}
        for cid in champion_ids
    ]
    _deck_unit_repo.save_all(deck_id, units)

    # deck_synergy 저장
    synergies = [{"trait_id": tid, "active_count": 2} for tid in trait_ids]
    _deck_synergy_repo.save_all(deck_id, synergies)

    # 캐리 유닛 추천 아이템 저장
    if item_ids and carry_id:
        from repository import DeckUnitRepository
        du_repo = DeckUnitRepository()
        du_list = du_repo.find_by_deck_id(deck_id)
        carry_unit = next((u for u in du_list if u["champion_id"] == carry_id), None)
        if carry_unit:
            items = [{"item_id": iid} for iid in item_ids]
            _rec_item_repo.save_all(carry_unit["id"], items)

    return deck_id


# ── 기타 유틸 ─────────────────────────────────────────

def get_all_items() -> list[dict]:
    return _item_repo.find_all()


