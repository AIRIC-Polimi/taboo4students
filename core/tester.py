import importlib
import importlib.util
import inspect
import time
import builtins
from pathlib import Path
from math import sqrt
import traceback
from tqdm import tqdm

from core.agent import Agent
from core.errors import AgentError, GuesserError
from core.guesser import Guesser
from core.rules import check_guess, check_hint
from core.answer_generation import LLM
from core.decorators import timeout

repo_root_folder = Path(__file__).parent.parent


def load_agent(module_path: str, llm: LLM):
    full_module_path = repo_root_folder / module_path
    if not Path(full_module_path).exists():
        raise ValueError(f"Agent module not found in path {full_module_path}")

    try:
        spec = importlib.util.spec_from_file_location("agent", full_module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        agents_classes = [
            cls_obj
            for _, cls_obj in inspect.getmembers(module)
            if inspect.isclass(cls_obj) and issubclass(cls_obj, Agent) and cls_obj != Agent
        ]
        if len(agents_classes) != 1:
            raise ValueError(f"Agent module must define only a single agent class ({full_module_path})")

        agent_class_methods = inspect.getmembers(agents_classes[0])
        agent_class_methods_names = [name for name, _ in agent_class_methods]
        for method_name in ["get_hint", "custom_similarity_search"]:
            if method_name not in agent_class_methods_names:
                raise ValueError(f"Agent class missing implementation of method {method_name}")

        # TODO: check for extra imports

        agent = agents_classes[0](llm=llm)
        return agent
    except ModuleNotFoundError as e:
        raise ValueError(f"Unable to import code for agent in path {full_module_path}")

@timeout(20)
def get_hint_with_timeout(agent: Agent, guess_word: str, taboo_list: list[str], level: int) -> str:
    try:
        hint = agent.get_hint(taboo_list=taboo_list, guess_word=guess_word, level=level)
    except Exception as e:
        raise AgentError(f"Failed to generate hint for word '{guess_word}'", original_error=e)
    return hint

def _test_sample(
    agent: Agent,
    guesser: Guesser,
    guess_word: str,
    taboo_list: list[str],
    hints_list: list,
    french_translations_dict: dict,
    level: int,
    verbose: bool = True,
) -> bool:
    def print(msg):
        if verbose:
            builtins.print(msg)

    print(f"Lvl{level} - Current guess word - taboo: {guess_word} - {taboo_list}")

    # Generate hint with the Agent that the player created
    try:
        hint = get_hint_with_timeout(agent=agent, guess_word=guess_word, taboo_list=taboo_list, level=level)
    except TimeoutError as e:
        raise AgentError(f"Timeout error when generating hint for word '{guess_word}'", original_error=e)

    # Check if hint respects the current level rules
    if check_hint(taboo_list=taboo_list, guess_word=guess_word, hint=hint, level=level, hints_list=hints_list, french_translations_dict=french_translations_dict):
        # Generate guess
        try:
            guess = guesser.get_guess(hint)
        except Exception as e:
            # TODO: catch errors related to content filter (to possibly award score differently)
            raise GuesserError(f"Guess generation failed for hint '{hint}'", original_error=e)

        # Check if guess respects the current level rules
        if check_guess(
            guess_word=guess_word, guess=guess, level=level, french_translations_dict=french_translations_dict
        ):
            print(f"Lvl{level} - Target: {guess_word} - Hint: {hint} - Guess: {guess}\n\n")
            return True
        else:
            print(f"Bad Guess! Lvl{level} - Target {guess_word} - Hint: {hint} - Guess: {guess}\n\n")
    else:
        print(f"Bad Hint lvl{level}: {guess_word} - Hint: {hint}")

    return False


def compute_score(results_by_level: dict) -> float:
    score = 0

    for level, results in results_by_level.items():
        # TODO: implement some proper scoring logic (e.g., do we want to weight levels differently, or treat incorrect answers and runtime errors in a different way?)
        score += results["correct"] * sqrt(level)

    return round(score, 1)


def test_solution(
    module_path: str,
    test_list: list,
    hints_list: list,
    french_translations_dict: dict,
    hints_db: dict,
    levels: list[int] = [1, 2, 3, 4],
    verbose: bool = True,
    model_name: str = "gpt-4o-mini",
    progress_bar_id: int | None = None,
):
    agent = load_agent(module_path, llm=LLM(hints_db=hints_db, model_name=model_name, verbose=verbose))
    guesser = Guesser(llm=LLM(hints_db=hints_db, model_name=model_name, verbose=verbose))

    def print(msg):
        if verbose:
            builtins.print(msg)

    results_by_level = {
        level: {"correct": 0, "incorrect": 0, "agent_error": 0, "guesser_error": 0, "uncaught_error": 0}
        for level in levels
    }

    # Test with the test_list
    start_time = time.time()

    use_tqdm = progress_bar_id is not None and not verbose
    if use_tqdm:
        progress_bar = tqdm(
            total=len(levels) * len(test_list), colour="#872452", position=progress_bar_id, desc=agent.get_name()
        )

    for level in levels:
        print(f"\nLevel {level}\n")
        for guess_word, taboo_list in test_list:
            try:
                success = _test_sample(
                    agent=agent,
                    guesser=guesser,
                    guess_word=guess_word,
                    taboo_list=taboo_list,
                    hints_list=hints_list,
                    french_translations_dict=french_translations_dict,
                    level=level,
                    verbose=verbose,
                )
                results_by_level[level]["correct" if success else "incorrect"] += 1
            except AgentError as e:
                print(e)
                if verbose:
                    traceback.print_exception(e.original_error)
                results_by_level[level]["agent_error"] += 1
            except GuesserError as e:
                print(e)
                if verbose:
                    traceback.print_exception(e.original_error)
                results_by_level[level]["guesser_error"] += 1
            except Exception as e:
                print(f"Uncaught error when guessing word '{guess_word}': {e}")
                results_by_level[level]["uncaught_error"] += 1

            if use_tqdm:
                progress_bar.update(1)

    if use_tqdm:
        progress_bar.display(msg=f"{agent.get_name()} COMPLETED")
        progress_bar.disable = True

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    accuracy = {
        level: f"{data['correct']}/{len(test_list)} ({round(data['correct'] / (max(1, len(test_list))) * 100, 2)}%)"
        for level, data in results_by_level.items()
    }
    print(f"Accuracy: {accuracy}")
    num_exceptions = sum(
        result["agent_error"] + result["guesser_error"] + result["uncaught_error"]
        for result in results_by_level.values()
    )

    return {
        "agent_name": agent.get_name(),
        "execution_time": execution_time,
        "raw_results": results_by_level,
        "accuracy": accuracy,
        "score": compute_score(results_by_level=results_by_level),
        "exceptions": num_exceptions,
    }
