import sys

lines = []
with open('import_opt.log', 'r', encoding='utf-16le') as f:
    for l in f:
        if 'import time' in l:
            lines.append(l)

lines = [l for l in lines if 'cumulative' not in l and '|' in l]
lines.sort(key=lambda x: int(x.split('|')[1].strip()) if len(x.split('|')) > 1 and x.split('|')[1].strip().isdigit() else 0, reverse=True)
print("".join(lines[:15]))
