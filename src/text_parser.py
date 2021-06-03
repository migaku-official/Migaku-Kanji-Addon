import re
import aqt

bracket_regex = re.compile(r'\[[^\[]+?\]')
html_regex = re.compile(r'<[^<]+?>')


cjk_ranges = [
   ( 0x4e00,  0x9faf),  # CJK unified ideographs
   ( 0x3400,  0x4dbf),  # CJK unified ideographs Extension A
   (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
   (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
   (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
   (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
   (0x2CEB0, 0x2EBEF),  # CJK Unified Ideographs Extension F
   (0x30000, 0x3134F),  # CJK Unified Ideographs Extension G
   ( 0xF900,  0xFAFF),  # CJK Compatibility Ideographs
   (0x2F800, 0x2FA1F), 	# CJK Compatibility Ideographs Supplement
]

def is_cjk(c):
   return any(s <= ord(c) <= e for (s,e) in cjk_ranges)

def has_cjk(word):
   return any(is_cjk(c) for c in word)


def filter_cjk(text):
   return filter(has_cjk, text)


def to_hiragana(text):
   parser = aqt.mw.Exporter.dictParser
   return parser.kaner(text, True)


def get_cjk_words(text, reading=False):
   exporter = aqt.mw.Exporter

   text = text.replace(' ', '')
   text = text.replace('&ensp', ' ')
   text = text.replace('\u2002', ' ')
   
   # Remove brackets (Anki media and migaku syntax)
   text = bracket_regex.sub('', text)

   # Remove HTML
   text = html_regex.sub('', text)

   # Parse text
   mecab_result = exporter.dictParser.getParsed(text)
   results = exporter.wordData(mecab_result)

   r = []
   for entry in results:
      dict_form = entry[7]
      if has_cjk(dict_form):
         if reading:
            dict_form_reading, *_ = exporter.dictionary.initSearch(dict_form)
            r.append( (dict_form, dict_form_reading) )
         else:
            r.append(dict_form)
   return r


def is_available():
   return hasattr(aqt.mw, 'Exporter')
