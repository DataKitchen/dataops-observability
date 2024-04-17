from peewee import CharField, Model


class FakeModelA(Model):
    foo = CharField()
    bar = CharField()
