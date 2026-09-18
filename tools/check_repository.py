#!/usr/bin/env python3
"""Offline checks for ROS package discovery, launch contracts and required assets."""
import ast
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
packages = {}
for manifest in ROOT.rglob('package.xml'):
    if any((p / 'CATKIN_IGNORE').exists() for p in manifest.parents if p != ROOT.parent):
        continue
    tree = ET.parse(manifest).getroot()
    name = tree.findtext('name')
    assert name not in packages, 'Duplicate ROS package: ' + name
    assert (manifest.parent / 'CMakeLists.txt').is_file(), str(manifest)
    packages[name] = manifest.parent
assert len(packages) == 13, sorted(packages)
assert not (ROOT / 'src/CMakeLists.txt').exists(), 'Do not nest a catkin workspace in this repository'

for launch in ROOT.rglob('*.launch'):
    ET.parse(launch)
for script in ROOT.glob('packages/**/scripts/*.py'):
    ast.parse(script.read_text(encoding='utf-8'), filename=str(script))
    assert script.read_bytes().startswith(b'#!/usr/bin/env python3'), str(script)

def find_path(value):
    match = re.fullmatch(r'\$\(find ([^)]+)\)(/.*)', value)
    if match:
        assert match[1] in packages, value
        result = packages[match[1]] / match[2].lstrip('/')
        assert result.exists(), str(result)
        return result

for name in ['xinghaitu_bringup', 'local_planner', 'far_planner', 'terrain_analysis', 'graph_decoder']:
    for launch in (packages[name] / 'launch').glob('*.launch'):
        tree = ET.parse(launch).getroot()
        args = [a.attrib['name'] for a in tree.findall('arg')]
        assert len(args) == len(set(args)), str(launch)
        for node in tree.iter():
            for value in node.attrib.values():
                for arg in re.findall(r'\$\(arg ([^)]+)\)', value):
                    assert arg in args, (launch, arg)
                if '$(find ' in value and '$(arg ' not in value:
                    find_path(value)
        for include in tree.iter('include'):
            target = find_path(include.attrib['file'])
            allowed = {a.attrib['name'] for a in ET.parse(target).getroot().findall('arg')}
            assert {a.attrib['name'] for a in include.findall('arg')} <= allowed, (launch, target)

path_dir = packages['local_planner'] / 'paths'
manifest = json.loads((path_dir / 'assets.json').read_text())
for filename, checksum in manifest['sha256'].items():
    data = (path_dir / filename).read_bytes().replace(b'\r\n', b'\n')
    assert hashlib.sha256(data).hexdigest() == checksum, filename
    header, body = data.decode().split('end_header\n', 1)
    count = int(re.search(r'element vertex (\d+)', header)[1])
    rows = body.strip().splitlines()
    assert len(rows) == count, filename
    if filename == 'pathList.ply':
        assert count == 343
        assert [int(row.split()[3]) for row in rows] == list(range(343))
        assert all(0 <= int(row.split()[4]) < 7 for row in rows)
with (path_dir / 'correspondences.txt').open() as stream:
    count = 0
    for count, row in enumerate(stream, 1):
        values = list(map(int, row.split()))
        assert values[0] == count - 1 and values[-1] == -1
        assert all(0 <= v < 343 for v in values[1:-1])
    assert count == 161 * 451

# A control path must never share FAST-LIO's trajectory topic.
local = ET.parse(packages['local_planner'] / 'launch/local_planner.launch').getroot()
for node_name in ['localPlanner', 'pathFollower']:
    node = next(n for n in local.findall('node') if n.attrib['name'] == node_name)
    assert any(m.attrib == {'from': '/path', 'to': '$(arg local_path_topic)'} for m in node.findall('remap'))
nav = ET.parse(packages['xinghaitu_bringup'] / 'launch/navigation.launch').getroot()
assert next(a for a in nav.findall('arg') if a.attrib['name'] == 'enable_cmd_vel_converter').attrib['default'] == 'false'

# Local documentation links and SVG assets stay valid after directory moves.
for doc in [ROOT / 'README.md', *ROOT.glob('docs/*.md')]:
    for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'):
            continue
        assert (doc.parent / target.split('#')[0]).exists(), (doc, target)
for svg in ROOT.glob('docs/assets/*.svg'):
    ET.parse(svg)
print('PASS: 13 packages, launch contracts, Python syntax, path dataset, topic isolation and documentation links')
