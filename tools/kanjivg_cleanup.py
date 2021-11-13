import os

kanjivg_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'addon',
    'kanjivg'
)

dir_it = os.listdir(kanjivg_dir)
count = len(dir_it)

for i, fname in enumerate(dir_it):

    print(F'[{i}/{count}] {fname}')

    if fname.endswith('.svg'):
        with open(os.path.join(kanjivg_dir, fname), 'r') as f:
            svg = f.read()

        idx = svg.find('<svg')
        if idx > 0:
            svg = svg[idx:]

        with open(os.path.join(kanjivg_dir, fname), 'w') as f:
            f.write(svg)

print('Done.')
