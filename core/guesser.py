from core.answer_generation import LLM


class Guesser:
    def __init__(self, llm: LLM):
        self.llm = llm

    def create_prompt_guess(self, hint):
        return f"Guess a single work based on the hint: {hint}. Respond only with the guess. Don't use punctuation or articles"

    def get_guess(self, hint):
        prompt = self.create_prompt_guess(hint=hint)
        guess = self.llm.generate_answer(prompt=prompt)
        guess = guess.strip().lower()
        return guess
