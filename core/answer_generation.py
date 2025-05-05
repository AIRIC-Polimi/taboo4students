from openai import AzureOpenAI, APIConnectionError, RateLimitError, APIStatusError, OpenAIError
from dotenv import load_dotenv
import json
import os
import builtins

# Load environment variables from .env file
load_dotenv()


class LLM:
    def __init__(self, hints_db: dict, model_name: str = "gpt-4o-mini", verbose: bool = True):
        self.model_name = model_name
        self.verbose = verbose
        self.client = AzureOpenAI()
        self.hints_db = hints_db

    def generate_answer(self, prompt: str):
        """Given a prompt, this function generates an answer using the LLM."""

        if len(prompt) > 450:
            raise ValueError("Prompt is too long. Please provide a shorter prompt. Maximum length is 450 characters.")

        messages = [
            {
                "role": "system",
                "content": "Sei un assistente che gioca a Taboo, il celebre gioco di parole. L'utente potrà chiederti di: (1) fornire indizi creativi che permettano alla tua squadra di indovinare una parola target senza mai utilizzare le parole vietate indicate, oppure (2) interpretare gli indizi ricevuti e tentare di indovinare correttamente la parola nascosta.",
            },
            {"role": "user", "content": prompt},
        ]

        def print(msg):
            if self.verbose:
                builtins.print(msg)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "text"},
                max_completion_tokens=300,
            )
            answer = response.choices[0].message.content
            return answer
        except APIConnectionError as e:
            print(f"Unable to reach the Azure OpenAI servers. Reason: {e.__cause__}")
            return "API_CONNECTION_ERROR"
        except RateLimitError as e:
            print("The maximum token per second has been reached; please slow down or request a new API KEY.")
            return "RATE_LIMIT_ERROR"
        except APIStatusError as e:
            if self._detect_content_filter_error(e):
                print(
                    f"The given prompt has triggered the Azure OpenAI content filter; please try to eliminate sensitive words. Prompt: '{prompt}'"
                )
                return "CONTENT_FILTER_ERROR"
            return f"API_ERROR_{e.status_code}"
        except OpenAIError as e:
            print(f"Unexpected OpenAI error: {e}")
            return "OPENAI_ERROR"

    def _detect_content_filter_error(self, error: APIStatusError) -> bool:
        if error.status_code != 400:
            return False

        try:
            response_dict = json.loads(error.response.read())
            return response_dict["error"]["code"] == "content_filter"
        except:
            return False

    def embed_text(self, text: str) -> list[float]:
        """Given a text, this function generates an embedding using the LLM."""
        response = self.client.embeddings.create(input=text, model="text-embedding-3-large")
        return response.data[0].embedding
