class FieldType:

    def __init__(self, t):
        self.t = t

    def to_json(self):
        return {'t': self.t}
