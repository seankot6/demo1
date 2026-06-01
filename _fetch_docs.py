import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')
base = 'https://rdb.red-soft.ru/docs/html/redexpert/%D0%A0%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D1%81%D1%82%D0%B2%D0%BE%20%D0%BF%D0%BE%20%D0%A0%D0%91%D0%94%20%D0%AD%D0%BA%D1%81%D0%BF%D0%B5%D1%80%D1%82/'
for page in ['index.html', 'search.html']:
    try:
        html = urllib.request.urlopen(base + page, timeout=15).read().decode('utf-8')
        links = re.findall(r'href="([^"]+\.html)"[^>]*>([^<]+)</a>', html)
        for href, text in links:
            t = re.sub(r'\s+', ' ', text).strip()
            if t and len(t) < 80:
                print(href, '|', t)
    except Exception as e:
        print('err', page, e)
