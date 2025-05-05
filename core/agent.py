from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_hint(self, taboo_list: list[str], guess_word: str, level: int) -> str: ...

    @abstractmethod
    def custom_similarity_search(self, query: str, k: int = 1) -> list[str]: ...
