import json, glob, os

base = '../public/cities'
print(f"{'City':15} {'Total':>7} {'Height':>7} {'H%':>4}  {'Year':>7} {'Y%':>4}")
print("-" * 55)
for path in sorted(glob.glob(f'{base}/**/buildings.geojson', recursive=True)):
    city = os.path.basename(os.path.dirname(path))
    with open(path, encoding='utf-8') as f:
        features = json.load(f)['features']
    total = len(features)
    has_h = sum(1 for f in features if f['properties'].get('height') not in (None, 0, ''))
    has_y = sum(1 for f in features if f['properties'].get('construction_year'))
    print(f"{city:15} {total:>7} {has_h:>7} {has_h*100//total:>3}%  {has_y:>7} {has_y*100//total:>3}%")
