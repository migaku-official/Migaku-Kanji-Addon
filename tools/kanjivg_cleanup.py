import os

kanjivg_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'addon',
    'kanjivg'
)

for fname in os.listdir(kanjivg_dir):

    if fname.endswith('.svg'):
        with open(os.path.join(kanjivg_dir, fname), 'r') as f:
            svg = f.read()

        idx = svg.find('<svg')
        if idx > 0:
            svg = svg[idx:]

        with open(os.path.join(kanjivg_dir, fname), 'w') as f:
            f.write(svg)
