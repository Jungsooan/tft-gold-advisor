import duckdb

con = duckdb.connect("tft_gold.duckdb")

print("=" * 50)
print("  SHOW TABLES")
print("=" * 50)
tables = con.execute("SHOW TABLES").fetchall()
for t in tables:
    cnt = con.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"  {t[0]:<25} {cnt} rows")

print()
print("=" * 50)
print("  SELECT * FROM champion LIMIT 5")
print("=" * 50)
rows = con.execute("SELECT id, name, cost, hp, atk FROM champion LIMIT 5").fetchall()
print(f"  {'id':<5} {'name':<15} {'cost':<6} {'hp':<6} {'atk':<6}")
print("  " + "-"*40)
for r in rows:
    print(f"  {r[0]:<5} {r[1]:<15} {r[2]:<6} {r[3]:<6} {r[4]:<6}")

print()
print("=" * 50)
print("  SELECT * FROM deck")
print("=" * 50)
rows = con.execute("SELECT id, name, total_cost, tier FROM deck").fetchall()
print(f"  {'id':<5} {'name':<25} {'cost':<6} {'tier':<6}")
print("  " + "-"*45)
for r in rows:
    print(f"  {r[0]:<5} {r[1]:<25} {r[2]:<6} {r[3]:<6}")

print()
print("=" * 50)
print("  3-Table LEFT JOIN")
print("  deck JOIN deck_unit JOIN champion")
print("  WHERE total_cost <= 20")
print("=" * 50)
rows = con.execute("""
    SELECT d.name, d.total_cost, ch.name, ch.cost, du.is_carry
    FROM deck d
    LEFT JOIN deck_unit du ON d.id = du.deck_id
    LEFT JOIN champion  ch ON du.champion_id = ch.id
    WHERE d.total_cost <= 20
    ORDER BY d.total_cost, du.is_carry DESC
""").fetchall()
print(f"  {'deck_name':<25} {'G':<4} {'champion':<15} {'코스트':<6} {'캐리'}")
print("  " + "-"*55)
for r in rows:
    print(f"  {r[0]:<25} {r[1]:<4} {r[2]:<15} {r[3]:<6} {'O' if r[4] else '-'}")

con.close()
