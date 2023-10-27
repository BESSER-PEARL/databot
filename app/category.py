class Category:

    def __init__(self, value: str):
        self.value: str = value
        self.synonyms: dict[str, list[str]] = {'en': []}
