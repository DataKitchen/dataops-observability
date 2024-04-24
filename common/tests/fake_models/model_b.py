from peewee import CharField, Model


class FakeModelB(Model):
    fizz = CharField()
    buzz = CharField()
