class Category:

    def __init__(self, value: str):
        self.value: str = str(value)
        self.synonyms: dict[str, list[str]] = {'en': []}

    def to_dict(self):
        return {
            'synonyms': self.synonyms['en']
        }

    def to_dict_simple(self):
        return {}
