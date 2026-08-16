from pathlib import Path
import yaml
root = Path('data')
for sub in ('feesten', 'heiligen'):
    print('===', sub, '===')
    for p in sorted((root / sub).glob('*.yaml')):
        d = yaml.safe_load(p.read_text(encoding='utf-8'))
        refs = d.get('referenties') or []
        for r in refs:
            print(d['id'], '|', r.get('bron_id') or r.get('label'), '|', r.get('url') or r.get('locator') or '-')
