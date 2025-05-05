from core.agent import Agent


class ChangeMyNameAgent(Agent):
    def get_name(self) -> str:
        return "INSERT_HERE_AGENT_NAME"

    def get_hint(self, taboo_list: list[str], guess_word: str, level: int) -> str:
        ### YOUR CODE HERE ###
        # You can call chatgpt like this:
        # hint = self.llm.generate_answer(prompt="what is the answer to life the universe and everything?")
        hint = "42"  # Example answer
        ### YOUR CODE HERE ###

        return hint

    def custom_similarity_search(self, query: str, k: int = 1) -> list[str]:
        ### YOUR CODE HERE ###
        # Get the embedding for the query
        # Calculate the cosine similarity usin numpy library
        # Get the top k hints
        # Return the hints
        ### YOUR CODE HERE ###
        pass

    ### You can add more methods here if you want to ###
    def random_method(self):
        pass
