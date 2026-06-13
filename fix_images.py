import urllib.request, ssl, duckdb

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
base = 'https://ddragon.leagueoflegends.com/cdn/15.10.1/img/champion'
con = duckdb.connect('tft_gold.duckdb')

fixes = [('초가스', 'Chogath'), ('누누', 'Nunu')]
for name, eng in fixes:
    path = f'images/champions/{eng.lower()}.png'
    url  = f'{base}/{eng}.png'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as r:
            open(path, 'wb').write(r.read())
        con.execute('UPDATE champion SET image_path=? WHERE name=?', [path, name])
        print(f'완료: {name}')
    except Exception as e:
        print(f'실패: {name} - {e}')

con.close()
