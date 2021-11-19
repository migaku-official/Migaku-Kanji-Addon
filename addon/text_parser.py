import os
import subprocess
import re

import anki


class MecabParser():

    def __init__(self):
        self.mecab_dir = os.path.join(os.path.dirname(__file__), 'mecab')
        self.mecab_bin = os.path.join(self.mecab_dir, 'mecab')
        self.mecab_dic = os.path.join(self.mecab_dir, 'unidic')
        self.mecab_rc = os.path.join(self.mecab_dir, 'unidic', 'mecabrc')

        self.mecab_env = os.environ.copy()
        self.mecab_env['LD_LIBRARY_PATH'] = self.mecab_dir
        self.mecab_env['DYLD_LIBRARY_PATH'] = self.mecab_dir

        self.mecab_extra_args = {}

        if anki.utils.isLin:
            self.mecab_bin += '-linux'
        elif anki.utils.isMac:
            self.mecab_bin += '-macos'
        elif anki.utils.isWin:
            self.mecab_bin += '-windows.exe'
            self.mecab_extra_args['creationflags'] = 0x08000000     # CREATE_NO_WINDOW
        else:
            raise NotImplementedError('Unsupported OS')

        self.mecab_options = [
            '-d', self.mecab_dic,
            '-r', self.mecab_rc,
            '-O', 'custom'
        ]

        self.mecab_process = None

    def start(self):
        if anki.utils.isLin or anki.utils.isMac:
            os.chmod(self.mecab_bin, 0o755)

        if self.mecab_process is None:
            self.mecab_process = subprocess.Popen(
                [self.mecab_bin] + self.mecab_options,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=self.mecab_env,
                **self.mecab_extra_args
            )

    def stop(self):
        if self.mecab_process is not None:
            self.mecab_process.kill()
            self.mecab_process = None

    def is_running(self):
        return (not self.mecab_process is None) and (self.mecab_process.poll() is None)

    def parse(self, text):
        assert self.is_running()

        self.mecab_process.stdin.write(text.encode('utf-8', errors='ignore') + b'\n')
        self.mecab_process.stdin.flush()

        results = []

        while True:
            mecab_result = self.mecab_process.stdout.readline().decode('utf-8').strip()
            if mecab_result == 'EOS':
                break
            result = mecab_result.split('\t')
            if len(result) == 3:
                i = result[1].find('-')
                if i >= 0:
                    result[1] = result[1][:i]
                results.append(result)

        return results


parser = MecabParser()
parser.start()



cjk_ranges = [
    ( 0x4e00,  0x9faf),     # CJK unified ideographs
    ( 0x3400,  0x4dbf),     # CJK unified ideographs Extension A
    (0x20000, 0x2A6DF),     # CJK Unified Ideographs Extension B
    (0x2A700, 0x2B73F),     # CJK Unified Ideographs Extension C
    (0x2B740, 0x2B81F),     # CJK Unified Ideographs Extension D
    (0x2B820, 0x2CEAF),     # CJK Unified Ideographs Extension E
    (0x2CEB0, 0x2EBEF),     # CJK Unified Ideographs Extension F
    (0x30000, 0x3134F),     # CJK Unified Ideographs Extension G
    ( 0xF900,  0xFAFF),     # CJK Compatibility Ideographs
    (0x2F800, 0x2FA1F),     # CJK Compatibility Ideographs Supplement
]

def is_cjk(c):
    return any(s <= ord(c) <= e for (s,e) in cjk_ranges)

def has_cjk(word):
    return any(is_cjk(c) for c in word)

def filter_cjk(text):
    return filter(has_cjk, text)


hiragana = list(
    'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすず'
    'せぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴ'
    'ふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろわ'
    'をんーゎゐゑゕゖゔゝゞ'
)

katakana = list(
    'ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズ'
    'セゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピ'
    'フブプヘベペホボポマミムメモャヤュユョヨラリルレロワ'
    'ヲンーヮヰヱヵヶヴヽヾ'
)

katakana_to_hiragana_map = dict(zip(
    list(map(ord, katakana)),
    hiragana
))

def to_hiragana(text: str):
    return text.translate(katakana_to_hiragana_map)


bracket_regex = re.compile(r'\[[^\[]+?\]')
html_regex = re.compile(r'<[^<]+?>')

def cleanup_text(text: str):
    text = text.replace(' ', '')
    text = text.replace('&ensp', ' ')
    text = text.replace('\u2002', ' ')

    # Remove brackets (Anki media and migaku syntax)
    text = bracket_regex.sub('', text)

    # Remove HTML
    text = html_regex.sub('', text)

    return text


def get_cjk_words(text, reading=False):
    text = cleanup_text(text)

    r = []
    for occurence, dict_form, dict_form_reading in parser.parse(text):
        if has_cjk(occurence) and has_cjk(dict_form):
            if reading:
                dict_form_reading = to_hiragana(dict_form_reading)
                r.append( (dict_form, dict_form_reading) )
            else:
                r.append(dict_form)
    return r


def is_available():
    return parser.is_running()
