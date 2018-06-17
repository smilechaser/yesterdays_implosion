'''
Test rig for generating models from YAML files.
'''

import os
import pprint
import weakref

import yaml

from errors import InvalidEntityException
from fields import FieldFactory


# pylint: disable=too-few-public-methods
class Model:
    '''Base class for all "things"'''

    @property
    def instance(self):
        return False


class Definition(Model):
    '''This is effectively the equivalent of a "class" keyword in python.'''

    @classmethod
    def create_instance(cls, name, data):

        return Factory(name, data)

    @property
    def name(self):
        return self.__class__.name


class Factory(Model):
    '''An instance of a Definition. Responsible for creating subtype
    instances.'''

    def __init__(self, name, data):

        self.name = name

        self.fields = data.get('fields', {}).copy()

    def create_instance(self, name, data):

        return Instance(self, name, data)

    def get_field(self, name):

        return self.fields.get(name)


class Instance(Model):
    '''A specific instance of a particular Definition. For instance once of
    these objects might be a "gun" of a Factory "Item".'''

    def __init__(self, parent, name, data):

        self.kind = parent.name
        self.name = name
        self.fields = FieldWrapper(parent)

        for k, val in data.items():

            self.fields.add(k, val)

    @property
    def instance(self):
        return True


class FieldWrapper:

    def __init__(self, template):

        self._fields = {}
        self._template = weakref.proxy(template)

    def add(self, k, val):

        field_meta = self._template.get_field(k)

        if not field_meta:
            raise Exception(
                f'Item "{self._template.name}" has no field "{k}".'
            )

        # create field using template field metadata
        self._fields[k] = FieldFactory().make_field(k, field_meta)

        # set the field's value
        self._fields[k].set(val)

    @property
    def as_dict(self):

        return {k: v.as_dict for k, v in self._fields.items()}


class ThingRegistry:

    def __init__(self):

        self.definitions = {
            'Definition': Definition
        }

        self.instances = []

    def load(self, filename):

        with open(filename, 'r') as fin:

            docs = yaml.load_all(fin)

            for doc in docs:

                kind, rest = extract_1kv(doc)

                name = rest.get('name')
                rest = rest.copy()
                rest.pop('name')

                thing = self.definitions[kind].create_instance(name, rest)

                if thing.name in self.definitions:
                    raise Exception(
                        f'Symbol {thing.name} already exists in symbol table.'
                    )

                if thing.instance:
                    self.instances.append(thing)
                else:
                    self.definitions[thing.name] = thing

    def get(self, name, kind):

        results = [
            thing for thing in self.instances
            if thing.name == name and thing.kind == kind]

        if len(results) > 1:
            raise Exception(
                'ERROR: Expected only 1 thing,'
                ' but got {}'.format(len(results)))

        return results[0] if results else None


def extract_1kv(data):

    if len(data) != 1:
        raise InvalidEntityException()

    root, rest = [(k, v) for k, v in data.items()][0]

    return root, rest


def main():

    things = ThingRegistry()

    print('Loading models...')

    for instance in os.listdir('objects/'):

        if not instance.endswith('.yaml'):
            continue

        print('\t{}'.format(instance))

        things.load(os.path.join('objects', instance))

    hosie = things.get('HOSIE', 'Attribute')

    pprint.pprint(hosie.fields.as_dict)

    pprint.pprint(things.get('gun', 'Item').fields.as_dict)


if __name__ == '__main__':

    main()
