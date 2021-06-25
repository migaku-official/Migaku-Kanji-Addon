from collections import namedtuple

import os
import shutil
import json

import anki
import aqt

from .util import addon_path
from . import config
from . import fonts



class CardTypeData:
    
    def __init__(self, model_name, fields):
        self.name = None        # Set automatically
        self.label = None       # Set automatically
        self.model_name = model_name
        self.fields = fields

    def __repr__(self):
        return self.name

    @property
    def deck_name(self):
        return config.get('card_type_deck').get(self.label)
    @deck_name.setter
    def deck_name(self, value):
        config.get('card_type_deck')[self.label] = value

    @property
    def add_primitives(self):
        return config.get('add_primitives').get(self.label, True)
    @add_primitives.setter
    def add_primitives(self, value):
        config.get('add_primitives')[self.label] = value

    @property
    def auto_card_creation(self):
        return config.get('auto_card_creation').get(self.label, False)
    @auto_card_creation.setter
    def auto_card_creation(self, value):
        config.get('auto_card_creation')[self.label] = value

    @property
    def auto_card_creation_msg(self):
        return config.get('auto_card_creation_msg').get(self.label, True)
    @auto_card_creation_msg.setter
    def auto_card_creation_msg(self, value):
        config.get('auto_card_creation_msg')[self.label] = value

    @property
    def auto_card_refresh(self):
        return config.get('auto_card_refresh').get(self.label, False)
    @auto_card_refresh.setter
    def auto_card_refresh(self, value):
        config.get('auto_card_refresh')[self.label] = value

    @property
    def show_readings_front(self):
        return config.get('card_show_readings_front').get(self.label, True)
    @show_readings_front.setter
    def show_readings_front(self, value):
        config.get('card_show_readings_front')[self.label] = value

    @property
    def words_max(self):
        return config.get('card_words_max').get(self.label, True)
    @words_max.setter
    def words_max(self, value):
        config.get('card_words_max')[self.label] = value

    @property
    def only_custom_keywords(self):
        return config.get('card_only_custom_keywords').get(self.label, False)
    @only_custom_keywords.setter
    def only_custom_keywords(self, value):
        config.get('card_only_custom_keywords')[self.label] = value

    @property
    def only_custom_stories(self):
        return config.get('card_only_custom_stories').get(self.label, False)
    @only_custom_stories.setter
    def only_custom_stories(self, value):
        config.get('card_only_custom_stories')[self.label] = value

    def model_id(self):
        return aqt.mw.col.models.id_for_name(self.model_name)

    # Returns a list of all cards belonging to this card type
    def find_card_ids(self):
        return aqt.mw.col.find_cards(F'"note:{self.model_name}"')

    # Updates the associated model (aka note type)
    def upsert_model(self):
        def model_file_data(name):
            path = addon_path('models', self.label, name)
            return open(path, 'r', encoding='UTF-8').read()

        # Get or create model
        model = aqt.mw.col.models.byName(self.model_name)
        if model is None:
            model = aqt.mw.col.models.new(self.model_name)

        # Assure required fields exist
        def field_exists(name):
            return any([fld['name'] == name for fld in model['flds']])

        for field_name in self.fields:
            if not field_exists(field_name):
                field = aqt.mw.col.models.new_field(field_name)
                aqt.mw.col.models.add_field(model, field)

        # Set CSS
        font_css = fonts.card_css()
        static_css = model_file_data('style.css')
        model['css'] = font_css + '\n\n' + static_css

        # Get or create standard template
        template_name = 'Standard'
        template = None
        for t in model['tmpls']:
            if t['name'] == template_name:
                template = t
                break
        if template is None:
            template = aqt.mw.col.models.new_template(template_name)
            model['tmpls'].append(template)

        # Compile settings
        settings = {
            'show_readings_front': self.show_readings_front,
            'words_max': self.words_max,
            'only_custom_keywords': self.only_custom_keywords,
            'only_custom_stories': self.only_custom_stories,
        }
        settings_html = F'<script>var settings = JSON.parse(\'{json.dumps(settings)}\');</script>'

        # Set template html
        template['qfmt'] = settings_html + '\n\n' + model_file_data('front.html')
        template['afmt'] = settings_html + '\n\n' + model_file_data('back.html')

        aqt.mw.col.models.save(model)



class CardTypeMeta(type):

    def __new__(cls, clsname, clsbases, clsdict):        
        cls.entries = {}

        for name in clsdict:
            ctd = clsdict[name]
            if type(ctd) == CardTypeData:
                label = name.lower()
                ctd.name = name
                ctd.label = label
                cls.entries[label] = ctd

        return super().__new__(cls, clsname, clsbases, clsdict)

    def __iter__(cls):
        return (cls.entries[label] for label in cls.entries)

    def __getitem__(cls, label):
        return cls.entries[label.lower()]

    def __len__(cls):
        return len(cls.entries)



class CardType(metaclass=CardTypeMeta):
    
    Recognition = CardTypeData(
        model_name='Migaku Kanji Recognition',
        fields=['Character', 'UserData', 'MigakuData', 'StrokeOrder'],
    )

    Production = CardTypeData(
        model_name='Migaku Kanji Production',
        fields=['Character', 'UserData', 'MigakuData', 'StrokeOrder'],
    )

    @classmethod
    def upsert_all_models(cls):
        for ctd in cls:
            ctd.upsert_model()
        fonts.assure_col_media()
