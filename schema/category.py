class Category:

    def __init__(self, value: str):
        self.value: str = str(value)
        self.synonyms: dict[str, list[str]] = {'en': []}

    def to_json(self):
        return {'value': self.value,
                'synonyms': self.synonyms}
