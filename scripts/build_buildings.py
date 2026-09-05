"""Build data/buildings.json and data/buildings.js: Overture buildings near the fire perimeters on the page.

The .js file assigns the same JSON to window.BUILDINGS_DATA so index.html can load it with a
script tag, which works from disk as well as from a web server.

Steps:
1. Read the fire perimeters and hyperspectral tiles embedded in index.html.
2. Download Overture buildings for the page's bounding box (skipped if the
   raw GeoJSON already exists).
3. Keep footprints within BUFFER_M of any perimeter and write a compact record
   per building with area, containing perimeter, distance to the nearest fire
   line, containing hyperspectral tile, and source datasets.

Run from the repository root:

    uv run --with "shapely>=2.0" --with pyproj --with overturemaps python scripts/build_buildings.py

The Overture release defaults to the latest; pass --release to pin one.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import pyproj
from shapely.geometry import shape
from shapely.ops import transform, unary_union

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'index.html'
RAW = ROOT / 'data' / 'overture_buildings_raw.geojson'
OUT = ROOT / 'data' / 'buildings.json'
BBOX = (-117.625, 47.683, -117.300, 47.832)
BUFFER_M = 300.0
SRC_BIT = {'Microsoft ML Buildings': 1, 'OpenStreetMap': 2, 'Esri Community Maps': 4}


def embedded_collections(html: str):
    """Return the FeatureCollections declared as constants in the page."""
    dec = json.JSONDecoder()
    out = {}
    for name in ('FIRE_GEOJSON', 'HSI_GEOJSON'):
        m = re.search(r'const %s = ' % name, html)
        if not m:
            sys.exit(f'{name} not found in index.html')
        out[name], _ = dec.raw_decode(html, m.end())
    return out


def download_raw(release: str | None):
    if RAW.exists():
        print('using existing', RAW)
        return
    cmd = ['overturemaps', 'download', '--bbox=%s' % ','.join(map(str, BBOX)),
           '-f', 'geojson', '-t', 'building', '-o', str(RAW)]
    if release:
        cmd += ['-r', release]
    print('running', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release', default=None, help='Overture release id, e.g. 2026-08-19.0')
    args = ap.parse_args()

    html = PAGE.read_text(encoding='utf-8', errors='ignore')
    cols = embedded_collections(html)
    fires = cols['FIRE_GEOJSON']['features']
    tiles = cols['HSI_GEOJSON']['features']

    RAW.parent.mkdir(exist_ok=True)
    download_raw(args.release)
    state = json.loads((RAW.with_suffix(RAW.suffix + '.state')).read_text()) if RAW.with_suffix(RAW.suffix + '.state').exists() else {}
    release = state.get('last_release') or args.release or 'unknown'

    to_m = pyproj.Transformer.from_crs(4326, 32611, always_xy=True).transform
    fire_m = [(f['properties']['name'], transform(to_m, shape(f['geometry']))) for f in fires]
    tile_m = [(t['properties']['name'], transform(to_m, shape(t['geometry']))) for t in tiles]
    zone = unary_union([g.buffer(BUFFER_M) for _, g in fire_m])

    rows, ms_version = [], None
    for f in json.load(open(RAW))['features']:
        g = shape(f['geometry'])
        gm = transform(to_m, g)
        c = gm.representative_point()
        if not zone.contains(c):
            continue
        p = f['properties']
        fire = next((n for n, fg in fire_m if fg.contains(c)), None)
        dist = min(fg.boundary.distance(c) for _, fg in fire_m)
        hsi = next((n for n, tg in tile_m if tg.contains(c)), None)
        src = 0
        for s in p.get('sources') or []:
            src |= SRC_BIT.get(s.get('dataset'), 0)
            if s.get('dataset') == 'Microsoft ML Buildings':
                ms_version = s.get('version')
        ring = g.exterior if g.geom_type == 'Polygon' else max(g.geoms, key=lambda x: x.area).exterior
        h = p.get('height')
        names = p.get('names') or {}
        rows.append({
            'id': p.get('id') or f.get('id'),
            'g': [[round(x, 6), round(y, 6)] for x, y in ring.coords],
            'h': round(h, 1) if isinstance(h, (int, float)) else None,
            'fl': p.get('num_floors'), 'c': p.get('class'), 'st': p.get('subtype'),
            'n': names.get('primary'), 's': src, 'a': int(round(gm.area)),
            'fire': fire, 'd': int(round(dist)), 'hsi': hsi,
            'v': p.get('version'), 'rs': p.get('roof_shape'),
        })

    out = {
        'meta': {
            'overture_release': release,
            'microsoft_version': ms_version,
            'bbox': list(BBOX),
            'buffer_m': BUFFER_M,
            'generated': __import__('datetime').date.today().isoformat(),
            'perimeters': [n for n, _ in fire_m],
            'note': ('Overture buildings within buffer_m of the fire perimeters on the page. '
                     'fire = perimeter containing the footprint; d = distance in m to the nearest fire line; '
                     'hsi = hyperspectral tile containing the footprint; s = source bitmask '
                     '(1 Microsoft ML Buildings, 2 OpenStreetMap, 4 Esri Community Maps); '
                     'a = footprint area m2; h = published height m.'),
        },
        'buildings': rows,
    }
    payload = json.dumps(out, separators=(',', ':'))
    OUT.write_text(payload, encoding='utf-8')
    OUT.with_suffix('.js').write_text(
        '/* generated by scripts/build_buildings.py; same content as buildings.json */\n'
        'window.BUILDINGS_DATA = ' + payload + ';\n', encoding='utf-8')
    inside = sum(1 for r in rows if r['fire'])
    print(f'wrote {OUT}: {len(rows)} buildings, {inside} inside a perimeter, {OUT.stat().st_size / 1e6:.2f} MB')


if __name__ == '__main__':
    main()
