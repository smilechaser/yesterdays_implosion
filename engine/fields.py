'''
This is a compendium of "data types" for use with fields.
'''

import inspect


class Field:

    name = None
    kind = None
    value = None

    IGNORED_FIELDS = ['name', 'kind']
    NAME_TRANSLATION_MAP = {
        'type': 'kind'
    }

    def __init__(self, name, meta):

        self.name = name

        for k, val in meta.items():

            k = self.NAME_TRANSLATION_MAP.get(k, k)

            if k in self.IGNORED_FIELDS:
                continue

            if k.startswith('_'):
                # TODO narrow
                raise Exception('Names cannot start with underscores')

            if not hasattr(self, k):
                # TODO narrow
                raise Exception(
                    '"{}" is not a recognized meta attribute for '
                    'attribute "{}" of type "{}".'
                    .format(k, self.name, self.kind))

            setattr(self, k, val)

        self.value = meta.get('value', self.default_value)

    @property
    def as_dict(self):

        return {
            'kind': self.kind,
            'value': self.value,
            **self.to_dict_aux()
        }

    # pylint: disable=no-self-use
    def to_dict_aux(self):

        return {}

    @property
    def default_value(self):
        return None

    def set(self, value):

        self.value = value


class StringField(Field):

    kind = 'string'
    unique = False

    @property
    def default_value(self):
        return ''


class IntegerField(Field):

    kind = 'integer'

    @property
    def default_value(self):
        return 0


class MapField(Field):

    kind = 'map'
    subtype = None

    @property
    def default_value(self):
        return {}

    def to_dict_aux(self):

        return {
            'subtype': self.subtype
        }


class ListField(Field):

    kind = 'list'
    subtype = None

    @property
    def default_value(self):
        return []

    def to_dict_aux(self):

        return {
            'subtype': self.subtype
        }


class ChoiceField(Field):

    kind = 'choice'
    multiple = False
    choices = None

    @property
    def default_value(self):
        return []

    def to_dict_aux(self):

        return {
            'multiple': self.multiple,
            'choices': self.choices
        }


class ReferenceField(Field):

    kind = 'reference'
    subtype = None


class SplatField(Field):

    kind = 'splat'

    @property
    def default_value(self):
        return None


class FieldFactory:

    field_types = None

    def __init__(self):

        #
        # build a map of Field subclasses
        #

        if not self.field_types:

            FieldFactory.field_types = {}

            for _, val in globals().items():

                if val == Field:
                    continue

                if not inspect.isclass(val):
                    continue

                if not issubclass(val, Field):
                    continue

                FieldFactory.field_types[val.kind] = val

    def make_field(self, name, field_data):

        kind = None

        if isinstance(field_data, str):
            kind = field_data
            field_data = {}
        else:
            kind = field_data['type']

        return self.field_types[kind](name, field_data)
