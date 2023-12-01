# Field types
TEXTUAL = 'textual'
NUMERIC = 'numeric'
DATETIME = 'datetime'
BOOLEAN = 'boolean'


class FieldType:

    def __init__(self, t):
        self.t = t
        # TODO: Add subtypes? (e.g., city, money, email address, etc)

    def to_json(self):
        return {'t': self.t}
