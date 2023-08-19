from collections import namedtuple

import os
import shutil
import json

import anki
import aqt

from .util import addon_path, col_media_path, read_web_file, read_web_file_with_includes
from . import config
from . import fonts


class CardTypeDataMeta(type):
    def __new__(mcls, clsname, clsbases, clsdict):
        cls = super().__new__(mcls, clsname, clsbases, clsdict)

        for property_name, property_default in clsdict.get(
            "config_properties", {}
        ).items():

            def make_property(property_name, property_default):
                config_propery_name = "card_type_" + property_name

                def get_property(cls_instance):
                    return config.get(config_propery_name, {}).get(
                        cls_instance.label, property_default
                    )

                def set_property(cls_instance, value):
                    config.get(config_propery_name, {})[cls_instance.label] = value

                return property(get_property, set_property)

            setattr(cls, property_name, make_property(property_name, property_default))

        return cls


class CardTypeData(metaclass=CardTypeDataMeta):
    config_properties = {
        "deck_name": None,
        "add_primitives": True,
        "auto_card_creation": False,
        "auto_card_creation_msg": True,
        "auto_card_refresh": False,
        "show_readings_front": True,
        "words_max": 4,
        "only_custom_keywords": False,
        "only_custom_stories": False,
        "hide_default_words": True,
        "hide_keywords": False,
        "stroke_order_mode": "fully_drawn",
        "stroke_order_show_numbers": False,
        "hide_readings_hover": False,
        "show_header": False,
        "show_radicals": False,
    }

    def __init__(self, model_name, fields):
        self.name = None  # Set automatically
        self.label = None  # Set automatically
        self.model_name = model_name
        self.fields = fields

    def __repr__(self):
        return self.name

    def model_id(self):
        return aqt.mw.col.models.id_for_name(self.model_name)

    # Returns a list of all cards belonging to this card type
    def find_card_ids(self):
        return aqt.mw.col.find_cards(f'"note:{self.model_name}"')

    # Updates the associated model (aka note type)
    def upsert_model(self):

        # Get or create model
        model = aqt.mw.col.models.byName(self.model_name)
        if model is None:
            model = aqt.mw.col.models.new(self.model_name)

        # Assure required fields exist
        def field_exists(name):
            return any([fld["name"] == name for fld in model["flds"]])

        for field_name in self.fields:
            if not field_exists(field_name):
                field = aqt.mw.col.models.new_field(field_name)
                aqt.mw.col.models.add_field(model, field)

        # Set CSS
        font_css = fonts.card_css()
        static_css = read_web_file("styles.css")
        model["css"] = font_css + "\n\n" + static_css

        # Get or create standard template
        template_name = "Standard"
        template = None
        for t in model["tmpls"]:
            if t["name"] == template_name:
                template = t
                break
        if template is None:
            template = aqt.mw.col.models.new_template(template_name)
            model["tmpls"].append(template)

        # Compile settings
        settings = {
            "show_readings_front": self.show_readings_front,
            "words_max": self.words_max,
            "only_custom_keywords": self.only_custom_keywords,
            "only_custom_stories": self.only_custom_stories,
            "hide_default_words": self.hide_default_words,
            "hide_keywords": self.hide_keywords,
            "stroke_order_mode": self.stroke_order_mode,
            "stroke_order_show_numbers": self.stroke_order_show_numbers,
            "hide_readings_hover": self.hide_readings_hover,
            "show_header": self.show_header,
            "show_radicals": self.show_radicals,
        }
        settings_html = f"""
            <script>
                var settings = JSON.parse('{json.dumps(settings)}');
            </script>
        """

        common_back_js = "<script>" + read_web_file("common_back.js") + "</script>\n\n"
        dmak_js = "<script>" + read_web_file("dmak.js") + "</script>\n\n"
        raphael_js = "<script>" + read_web_file("raphael.js") + "</script>\n\n"
        japanese_util_js = "<script>" + read_web_file("japanese-util.js") + "</script>\n\n"

        # Set template html
        template["qfmt"] = (
            settings_html + "\n\n" +
            japanese_util_js +
            read_web_file_with_includes(f"front-{self.label}.html")
        )
        template["afmt"] = (
            settings_html + "\n\n" +
            dmak_js +
            raphael_js +
            japanese_util_js +
            common_back_js +
            read_web_file_with_includes(f"back-{self.label}.html")
        )

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
        model_name="Migaku Kanji Recognition",
        fields=["Character", "UserData", "MigakuData", "StrokeOrder"],
    )

    Production = CardTypeData(
        model_name="Migaku Kanji Production",
        fields=["Character", "UserData", "MigakuData", "StrokeOrder"],
    )

    @classmethod
    def assure_global_col_media(cls):
        fonts.assure_col_media()

        for f in os.listdir(addon_path("collection")):
            shutil.copy(addon_path("collection", f), col_media_path(f))

    @classmethod
    def upsert_all_models(cls):
        for ctd in cls:
            ctd.upsert_model()
        cls.assure_global_col_media()
