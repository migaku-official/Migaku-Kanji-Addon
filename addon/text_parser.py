import os
import subprocess
import re
import requests
import zipfile

import anki
import aqt

from . import util


class MecabParser():

    def __init__(self):
        self.mecab_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mecab'))
        self.mecab_bin = os.path.join(self.mecab_dir, 'mecab')
        self.mecab_dic = util.user_path('dic')
        self.mecab_rc = os.path.join(self.mecab_dir, 'mecabrc')

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
            '-O', 'migaku_kanji',
        ]

        self.mecab_process = None

    def start(self):
        self.stop()

        if anki.utils.isLin or anki.utils.isMac:
            os.chmod(self.mecab_bin, 0o755)

        if self.mecab_process is None:
            self.mecab_process = subprocess.Popen(
                [self.mecab_bin] + self.mecab_options,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=-1,
                env=self.mecab_env,
                **self.mecab_extra_args
            )

    def stop(self):
        if self.mecab_process is not None:
            # Properly close the process
            # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
            try:
                self.mecab_process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                self.mecab_process.kill()
                self.mecab_process.communicate()

            self.mecab_process.kill()
            self.mecab_process = None

    def is_running(self):
        return (not self.mecab_process is None) and (self.mecab_process.poll() is None)

    def parse(self, text):
        assert self.is_running()

        text = text.replace('\n', ' ')

        self.mecab_process.stdin.write(text.encode('utf-8', errors='ignore') + b'\n')
        self.mecab_process.stdin.flush()

        results = []

        while True:
            mecab_result = self.mecab_process.stdout.readline().decode('utf-8', 'replace').strip()
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


class DicDownloader(aqt.qt.QObject):

    DOWNLOAD_URI = 'https://migaku-public-data.migaku.com/kanji_dict.zip'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.make_avaialble()

    def is_available(self):
        return os.path.exists(util.user_path('dic'))

    def make_avaialble(self):
        if not self.is_available():
            self.start_download()

    def start_download(self):
        class DownloadThread(aqt.qt.QThread):
            def __init__(self, target=None, parent=None):
                super().__init__(parent)
                self.target = target

            def run(self):
                self.target()

        aqt.mw.progress.start(label='Downloading Migaku Kanji Parsing Dictionary', max=100)

        download_thread = DownloadThread(self._download, self.parent())
        download_thread.finished.connect(self.finished_download)
        download_thread.start()

    def finished_download(self):
        aqt.mw.progress.finish()

        if not self.is_available():
            util.error_msg(
                aqt.mw,
                'Downloading Migaku Kanji Parsing Dictionary failed.\n\n'
                'It is required for for most functionality of the add-on.\n\n'
                'Please make sure that you are connected to the internet and restart Anki.\n\n'
                'It only has to be downloaded once.'
            )
        else:
            parser.start()

    def _download(self):
        def fmt_kb(n):
            return F'{n//1000}kB'

        util.assure_user_dir()
        download_path = util.user_path('dic.zip')

        def delete_download():
            try:
                os.remove(download_path)
            except:
                pass

        try:
            with open(download_path, 'wb') as f:
                with requests.get(self.DOWNLOAD_URI, stream=True) as r:
                    total = int(r.headers['Content-Length'])
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pos = f.tell()

                            label = F'Downloading Migaku Kanji Parsing Dictionary\n({fmt_kb(pos)}/{fmt_kb(total)})'

                            aqt.mw.taskman.run_on_main(
                                lambda: aqt.mw.progress.update(value=pos, max=total, label=label)
                            )
        except requests.HTTPError:
            delete_download()
            return

        # extract dic from downloaded zip into user_data
        aqt.mw.taskman.run_on_main(
            lambda: aqt.mw.progress.update(value=0, max=0, label='Extracting Migaku Kanji Parsing Dictionary')
        )

        with zipfile.ZipFile(download_path) as zf:
            zf.extractall(util.user_path())

        delete_download()

dic_downloader = DicDownloader(aqt.mw)



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
