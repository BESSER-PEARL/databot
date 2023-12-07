class Category:

    def __init__(self, value: str):
        self.value: str = str(value)
        self.synonyms: dict[str, list[str]] = {'en': []}

    def to_json(self):
        if self.synonyms['en']:
            return {
                # 'value': self.value,
                'synonyms': self.synonyms['en']
            }
        else:
            return {}
