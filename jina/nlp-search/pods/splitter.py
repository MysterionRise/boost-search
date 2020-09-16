from typing import Dict

from jina.executors.crafters import BaseCrafter


class Splitter(BaseCrafter):
    def craft(self, text: str, *args, **kwargs) -> Dict:
        word, definitions = text.split('+-=')
        return dict(text=definitions, meta_info=word.encode())