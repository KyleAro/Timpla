import json
from pathlib import Path
p=Path(__file__).parent;a=json.loads((p/'annotations.json').read_text(encoding='utf-8'))
for i in [476,601,620]:a[str(i)]['deps'].append('Squid ink/ink sac is retained from the listed squid and used in the sauce; it is not an independent second purchase. Preserve the squid and reserved-ink expression/state.')
for i in [198,407,506,543]:a[str(i)]['deps'].append('Souring fruit juice/pulp is extracted from the listed whole fruit in the method and returned to the same soup; do not treat that extract as a separate purchase.')
for i in [305,627,640]:a[str(i)]['notes'].append('Nonfood skewers, twine and leaf wrapping/lining are preparation materials, not additional edible requirements or automatic food gaps.')
(p/'annotations.json').write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
