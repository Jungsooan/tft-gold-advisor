import flet as ft
import os
from database import init_db
import service as svc

TIER_BG  = {"S": ft.Colors.YELLOW_700, "A": ft.Colors.BLUE_400,
            "B": ft.Colors.GREEN_500,  "C": ft.Colors.GREY_500}
COST_CLR = {1: ft.Colors.GREY_500, 2: ft.Colors.GREEN_600,
            3: ft.Colors.BLUE_600, 4: ft.Colors.PURPLE_600,
            5: ft.Colors.AMBER_700}

def small_tag(text):
    return ft.Container(
        content=ft.Text(text, size=10),
        bgcolor=ft.Colors.BLUE_50,
        border=ft.Border.all(1, ft.Colors.BLUE_200),
        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
        border_radius=8,
    )

def main(page: ft.Page):
    page.title = "TFT Gold Advisor"
    page.padding = 0
    try:
        page.window.width  = 960
        page.window.height = 720
    except Exception:
        pass

    init_db()

    snack_bar = ft.SnackBar(content=ft.Text(""))
    page.overlay.append(snack_bar)

    def show_snack(msg):
        snack_bar.content = ft.Text(msg)
        snack_bar.open = True
        page.update()

    detail_body = ft.Column([], width=440, tight=True, scroll=ft.ScrollMode.AUTO)
    detail_dlg  = ft.AlertDialog(
        modal=True,
        title=ft.Text("덱 상세"),
        content=detail_body,
        actions=[ft.TextButton("닫기", on_click=lambda e: close_detail())],
        open=False,
    )
    page.overlay.append(detail_dlg)

    def close_detail():
        detail_dlg.open = False
        page.update()

    def open_detail(deck):
        detail = svc.get_deck_detail(deck["deck_id"])
        if not detail:
            return
        champ_rows = []
        for c in detail.get("champions", []):
            img_p = c.get("image_path") or ""
            img_w = (
                ft.Image(src=img_p, width=36, height=36,
                        border_radius=4)
                if img_p and os.path.exists(img_p)
                else ft.Container(
                    content=ft.Text(c["name"][:2], size=9, color=ft.Colors.WHITE,
                                   text_align=ft.TextAlign.CENTER),
                    bgcolor=COST_CLR.get(c["cost"], ft.Colors.GREY_400),
                    border_radius=4, width=36, height=36,
                    alignment=ft.Alignment(0, 0),
                )
            )
            champ_rows.append(ft.Row([
                img_w,
                ft.Text("★캐리" if c["is_carry"] else "     ", size=10,
                        color=ft.Colors.AMBER_600, width=40),
                ft.Text(c["name"], size=12, expand=True,
                       weight=ft.FontWeight.BOLD if c["is_carry"] else ft.FontWeight.NORMAL),
                ft.Text(f"{c['cost']}코", size=11,
                       color=COST_CLR.get(c["cost"], ft.Colors.GREY_400)),
                ft.Text(f"Lv{c['star_level']}", size=11, color=ft.Colors.AMBER_600),
            ]))
        trait_rows = [
            ft.Row([
                ft.Text(t["trait_name"], size=12, weight=ft.FontWeight.BOLD,
                       color=ft.Colors.GREEN_700, expand=True),
                ft.Text(f"{t['active_count']}개 활성", size=11),
                ft.Text(f"발동:{t['thresholds']}", size=11, color=ft.Colors.GREY_500),
            ]) for t in detail.get("traits", [])
        ]
        detail_dlg.title = ft.Text(detail["name"], weight=ft.FontWeight.BOLD)
        detail_body.controls = [
            ft.Row([small_tag(f"티어 {detail.get('tier') or 'B'}"),
                   small_tag(f"{detail['total_cost']}G"),
                   small_tag(detail.get("patch_version") or "")]),
            ft.Text(detail.get("memo") or "", size=11, color=ft.Colors.GREY_600),
            ft.Divider(),
            ft.Text("구성 챔피언", size=13, weight=ft.FontWeight.BOLD),
            *champ_rows,
            ft.Divider(),
            ft.Text("핵심 특성", size=13, weight=ft.FontWeight.BOLD),
            *trait_rows,
        ]
        detail_dlg.open = True
        page.update()

    # ── TAB 1: 덱 추천 ────────────────────────────
    state      = {"gold": 25, "tier": "전체"}
    gold_label = ft.Text("25 G", size=22, weight=ft.FontWeight.BOLD,
                         color=ft.Colors.AMBER_700)
    count_text = ft.Text("", size=11, color=ft.Colors.GREY_500)
    deck_lv    = ft.ListView(expand=True, spacing=8,
                             padding=ft.Padding(left=10, right=10, top=6, bottom=6))
    tier_row   = ft.Row(spacing=6)

    def build_deck_card(deck):
        tier = deck.get("tier") or "B"
        return ft.GestureDetector(
            on_tap=lambda e, d=deck: open_detail(d),
            content=ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=ft.Padding(left=14, right=14, top=14, bottom=14),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(deck["deck_name"], size=14,
                                   weight=ft.FontWeight.BOLD, expand=True),
                            ft.Container(
                                content=ft.Text(f"{deck['total_cost']}G",
                                               size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.AMBER_100,
                                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                border_radius=6,
                            ),
                            ft.Container(
                                content=ft.Text(tier, size=11, color=ft.Colors.WHITE,
                                               weight=ft.FontWeight.BOLD),
                                bgcolor=TIER_BG.get(tier, ft.Colors.GREY_400),
                                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                border_radius=6,
                            ),
                        ]),
                        ft.Text(deck.get("playstyle") or "", size=11,
                               color=ft.Colors.GREY_600),
                        ft.Row([small_tag(f"{t['trait_name']} {t['active_count']}")
                               for t in deck.get("traits", [])],
                              wrap=True, spacing=4),
                    ], spacing=5),
                ),
            ),
        )

    def refresh_decks():
        tier  = state["tier"] if state["tier"] != "전체" else None
        decks = svc.get_decks_by_gold(state["gold"], tier)
        deck_lv.controls.clear()
        if not decks:
            deck_lv.controls.append(
                ft.Container(
                    content=ft.Text("이 골드로 가능한 덱이 없습니다.",
                                   text_align=ft.TextAlign.CENTER,
                                   color=ft.Colors.GREY_400, size=13),
                    alignment=ft.Alignment(0, 0), expand=True,
                )
            )
        else:
            for d in decks:
                deck_lv.controls.append(build_deck_card(d))
        count_text.value = f"{len(decks)}개 덱 추천됨"
        page.update()

    def on_gold_change(e):
        state["gold"] = int(e.control.value)
        gold_label.value = f"{state['gold']} G"
        refresh_decks()

    TIERS = ["전체", "S", "A", "B", "C"]

    def on_tier_click(tier, idx):
        state["tier"] = tier
        for i, con in enumerate(tier_row.controls):
            sel = (i == idx)
            con.bgcolor = ft.Colors.BLUE_600 if sel else ft.Colors.GREY_200
            con.content.color = ft.Colors.WHITE if sel else ft.Colors.BLACK87
        refresh_decks()

    for i, t in enumerate(TIERS):
        tier_row.controls.append(
            ft.Container(
                content=ft.Text(t, size=12,
                    color=ft.Colors.WHITE if t=="전체" else ft.Colors.BLACK87,
                    weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLUE_600 if t=="전체" else ft.Colors.GREY_200,
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                border_radius=6,
                on_click=lambda e, t=t, i=i: on_tier_click(t, i),
            )
        )

    tab1 = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("현재 골드", size=13), gold_label,
                       ft.Container(expand=True), count_text]),
                ft.Slider(min=0, max=100, value=25, divisions=20,
                         on_change=on_gold_change),
            ], spacing=2),
            padding=ft.Padding(left=12, right=12, top=10, bottom=4),
        ),
        ft.Container(
            content=ft.Row([ft.Text("티어:", size=12, color=ft.Colors.GREY_600),
                           tier_row]),
            padding=ft.Padding(left=12, right=12, top=4, bottom=4),
        ),
        ft.Divider(height=1),
        deck_lv,
    ], expand=True, spacing=0)

    # ── TAB 2: 챔피언 ────────────────────────────
    champ_wrap = ft.Row(wrap=True, spacing=8, run_spacing=8)
    champ_lv   = ft.ListView(controls=[champ_wrap], expand=True, padding=10)
    cost_btns  = ft.Row(spacing=6, wrap=True)

    def refresh_champs(cost=0):
        champs = svc.get_all_champions(cost)
        champ_wrap.controls.clear()
        for c in champs:
            img_path = c.get("image_path") or ""
            img_widget = (
                ft.Image(src=img_path, width=56, height=56,
                        border_radius=6)
                if img_path and os.path.exists(img_path)
                else ft.Container(
                    content=ft.Text(c["name"][:2], size=12, color=ft.Colors.WHITE,
                                   text_align=ft.TextAlign.CENTER),
                    bgcolor=COST_CLR.get(c["cost"], ft.Colors.GREY_400),
                    border_radius=6, width=56, height=56,
                    alignment=ft.Alignment(0, 0),
                )
            )
            champ_wrap.controls.append(
                ft.Container(
                    width=145, height=108,
                    border=ft.Border.all(1, ft.Colors.GREY_200),
                    border_radius=8, padding=8,
                    content=ft.Column([
                        img_widget,
                        ft.Text(c["name"], size=10, weight=ft.FontWeight.BOLD,
                               text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{c['cost']}코스트", size=9,
                               color=COST_CLR.get(c["cost"], ft.Colors.GREY_400),
                               text_align=ft.TextAlign.CENTER),
                        ft.Text(f"HP {c['hp']}  ATK {c['atk']}", size=8,
                               color=ft.Colors.GREY_500,
                               text_align=ft.TextAlign.CENTER),
                    ], spacing=2,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )
        page.update()

    for c in [0, 1, 2, 3, 4, 5]:
        label_c = "전체" if c == 0 else f"{c}코스트"
        cost_btns.controls.append(
            ft.GestureDetector(
                on_tap=lambda e, c=c: refresh_champs(c),
                content=ft.Container(
                    content=ft.Text(label_c, size=11, color=ft.Colors.BLACK87),
                    bgcolor=ft.Colors.GREY_200,
                    padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                    border_radius=5,
                ),
            )
        )

    tab2 = ft.Column([
        ft.Container(content=cost_btns,
                    padding=ft.Padding(left=10, right=10, top=8, bottom=8)),
        ft.Divider(height=1),
        champ_lv,
    ], expand=True, spacing=0)

    # ── TAB 3: 특성 ────────────────────────────
    trait_col = ft.Column([], spacing=4)
    trait_lv  = ft.ListView(controls=[trait_col], expand=True, padding=10)

    TYPE_CLR = {"계열": ft.Colors.BLUE_700, "직업": ft.Colors.GREEN_700}
    TYPE_BG  = {"계열": ft.Colors.BLUE_50,  "직업": ft.Colors.GREEN_50}

    def load_traits():
        traits = svc.get_all_traits()
        trait_col.controls.clear()
        for t in traits:
            expanded = [False]
            clr  = TYPE_CLR.get(t.get("trait_type",""), ft.Colors.GREY_700)
            bg   = TYPE_BG.get(t.get("trait_type",""),  ft.Colors.GREY_50)
            tiers = []
            tier_labels = [("브론즈", t.get("tier_bronze")),
                           ("실버",   t.get("tier_silver")),
                           ("골드",   t.get("tier_gold")),
                           ("프리즘", t.get("tier_prismatic"))]
            tier_colors = [ft.Colors.BROWN_400, ft.Colors.GREY_500,
                           ft.Colors.AMBER_600, ft.Colors.PURPLE_400]
            for (lbl, val), tcl in zip(tier_labels, tier_colors):
                if val:
                    tiers.append(
                        ft.Row([
                            ft.Container(
                                content=ft.Text(lbl, size=9, color=ft.Colors.WHITE,
                                               weight=ft.FontWeight.BOLD),
                                bgcolor=tcl,
                                padding=ft.Padding(left=6,right=6,top=2,bottom=2),
                                border_radius=4,
                                width=44,
                            ),
                            ft.Text(val, size=10, color=ft.Colors.GREY_700, expand=True),
                        ], spacing=8)
                    )
            detail = ft.Container(
                content=ft.Column([
                    ft.Text(t.get("description") or "", size=11,
                           color=ft.Colors.GREY_600),
                    ft.Divider(height=6),
                    *tiers,
                ], spacing=4),
                padding=ft.Padding(left=12, right=12, top=8, bottom=10),
                bgcolor=ft.Colors.GREY_50,
                visible=False,
            )
            def toggle(e, d=detail, ex=expanded):
                ex[0] = not ex[0]
                d.visible = ex[0]
                page.update()
            trait_col.controls.append(ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(t.get("trait_type",""), size=9,
                                           color=ft.Colors.WHITE,
                                           weight=ft.FontWeight.BOLD),
                            bgcolor=clr,
                            padding=ft.Padding(left=6,right=6,top=2,bottom=2),
                            border_radius=4,
                        ),
                        ft.Text(t["name"], size=13, weight=ft.FontWeight.BOLD,
                               color=clr, expand=True),
                        ft.Text(f"발동: {t['thresholds']}", size=11,
                               color=ft.Colors.GREY_500),
                        ft.Text("▼" if not expanded[0] else "▲",
                               size=11, color=ft.Colors.GREY_400),
                    ], spacing=8),
                    bgcolor=bg,
                    padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.3, clr)),
                    border_radius=8,
                    on_click=toggle,
                ),
                detail,
            ], spacing=2))
        page.update()

    tab3 = ft.Column([
        ft.Container(
            content=ft.Text("특성(시너지) 목록 - 세트 17 Space Gods",
                           size=14, weight=ft.FontWeight.BOLD),
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
        ),
        ft.Divider(height=1),
        trait_lv,
    ], expand=True, spacing=0)

    # ── TAB 4: 덱 등록 ────────────────────────────
    f_name  = ft.TextField(label="덱 이름", expand=True)
    f_cost  = ft.TextField(label="총 코스트", hint_text="비워두면 자동 계산", width=160)
    f_tier  = ft.Dropdown(label="티어", width=100,
                          options=[ft.DropdownOption(x) for x in ["S","A","B","C"]],
                          value="A")
    f_style = ft.TextField(label="운영 스타일", expand=True)
    f_patch = ft.TextField(label="패치", value="17.5b", width=100)
    f_memo  = ft.TextField(label="메모", multiline=True, min_lines=2, expand=True)

    champ_cb_row = ft.Row(wrap=True, spacing=4, run_spacing=4)
    trait_cb_row = ft.Row(wrap=True, spacing=4, run_spacing=4)
    carry_rg     = ft.RadioGroup(content=ft.Row(wrap=True, spacing=4, run_spacing=4))
    form_state   = {"champ_data": [], "trait_data": [], "built": False}

    def build_form():
        if form_state["built"]:
            return
        champs = svc.get_all_champions()
        traits = svc.get_all_traits()
        form_state["champ_data"] = [
            {"id": c["id"],
             "cb": ft.Checkbox(label=f"{c['name']}({c['cost']}코)", value=False)}
            for c in champs
        ]
        form_state["trait_data"] = [
            {"id": t["id"],
             "cb": ft.Checkbox(label=t["name"], value=False)}
            for t in traits
        ]
        champ_cb_row.controls = [c["cb"] for c in form_state["champ_data"]]
        trait_cb_row.controls = [t["cb"] for t in form_state["trait_data"]]
        carry_rg.content.controls = [
            ft.Radio(value=str(c["id"]), label=c["name"]) for c in champs
        ]
        if champs:
            carry_rg.value = str(champs[0]["id"])
        form_state["built"] = True
        page.update()

    def on_save(e):
        if not f_name.value.strip():
            show_snack("덱 이름을 입력하세요.")
            return
        sel_champs = [c["id"] for c in form_state["champ_data"] if c["cb"].value]
        sel_traits = [t["id"] for t in form_state["trait_data"] if t["cb"].value]
        try:
            cost_val = int(f_cost.value) if f_cost.value.strip() else None
        except ValueError:
            cost_val = None
        carry_id = (int(carry_rg.value) if carry_rg.value
                    else (sel_champs[0] if sel_champs else 0))
        data = {
            "name": f_name.value.strip(),
            "total_cost": cost_val,
            "tier": f_tier.value or "B",
            "playstyle": f_style.value,
            "patch_version": f_patch.value or "17.5b",
            "memo": f_memo.value,
        }
        new_id = svc.save_deck(data, sel_champs, carry_id, sel_traits)
        show_snack(f"'{data['name']}' 저장 완료 (ID:{new_id})")
        f_name.value = ""
        f_cost.value = ""
        f_memo.value = ""
        for c in form_state["champ_data"]: c["cb"].value = False
        for t in form_state["trait_data"]: t["cb"].value = False
        refresh_decks()
        page.update()

    tab4 = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([f_name, f_cost, f_tier, f_patch]),
                ft.Row([f_style, f_memo]),
                ft.Divider(),
                ft.Text("구성 챔피언 선택", size=12, weight=ft.FontWeight.BOLD),
                ft.Container(content=champ_cb_row, height=130,
                            border=ft.Border.all(1, ft.Colors.GREY_200),
                            border_radius=6, padding=8),
                ft.Divider(),
                ft.Text("캐리 유닛", size=12, weight=ft.FontWeight.BOLD),
                ft.Container(content=carry_rg, height=90,
                            border=ft.Border.all(1, ft.Colors.GREY_200),
                            border_radius=6, padding=8,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE),
                ft.Divider(),
                ft.Text("핵심 특성 선택", size=12, weight=ft.FontWeight.BOLD),
                trait_cb_row,
                ft.Divider(),
                ft.GestureDetector(
                    on_tap=on_save,
                    content=ft.Container(
                        content=ft.Text("덱 저장", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.BLUE_600,
                        padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                        border_radius=8,
                    ),
                ),
            ], spacing=8),
            padding=12,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    # ── 커스텀 탭바 ────────────────────────────
    tab_labels  = ["덱 추천", "챔피언", "특성", "덱 등록"]
    tab_contents = [tab1, tab2, tab3, tab4]
    tab_btns    = []
    content_area = ft.Container(content=tab1, expand=True)

    cur_tab_idx = [0]

    def switch_tab(idx):
        cur_tab_idx[0] = idx
        content_area.content = tab_contents[idx]
        for i, btn in enumerate(tab_btns):
            sel = (i == idx)
            btn.style = ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_700 if sel else ft.Colors.GREY_200,
                color=ft.Colors.WHITE      if sel else ft.Colors.BLACK,
            )
        if idx == 1: refresh_champs(0)
        elif idx == 2: load_traits()
        elif idx == 3: build_form()
        page.update()

    for i, label in enumerate(tab_labels):
        tab_btns.append(
            ft.Container(
                content=ft.Text(label, size=12,
                    color=ft.Colors.WHITE if i==0 else ft.Colors.BLACK87,
                    weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.BLUE_700 if i==0 else ft.Colors.GREY_200,
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border_radius=6,
                on_click=lambda e, i=i: switch_tab(i),
            )
        )

    page.add(
        ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("TFT Gold Advisor", size=18,
                           weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
                    ft.Container(expand=True),
                    ft.Text("Set 17 Space Gods  17.5b",
                           size=11, color=ft.Colors.GREY_500),
                ]),
                bgcolor=ft.Colors.BLUE_50,
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            ),
            ft.Container(
                content=ft.Row(tab_btns, spacing=4),
                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
            ),
            content_area,
        ], expand=True, spacing=0)
    )

    refresh_decks()


ft.app(target=main)
