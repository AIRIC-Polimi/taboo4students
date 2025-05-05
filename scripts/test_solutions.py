import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from multiprocessing import Pool, Manager
import traceback
import json

from tqdm import tqdm

from core.tester import test_solution


def _test_solution_multiprocessing(parameters):
    (
        id,
        agent_module_path,
        test_list,
        test_hints_level3,
        french_translations_dict,
        hints_db,
        levels,
        verbose,
        model_name,
    ) = parameters
    try:
        return test_solution(
            module_path=agent_module_path,
            test_list=test_list,
            hints_list=test_hints_level3,
            french_translations_dict=french_translations_dict,
            hints_db=hints_db,
            levels=levels,
            verbose=verbose,
            model_name=model_name,
            progress_bar_id=id,
        )
    except Exception as e:
        if verbose:
            traceback.print_exception(e)
            print(f"There was an uncaught error while running agent {agent_module_path}: {e}")
        return agent_module_path, e


def main():
    repo_folder = Path(__file__).parent.parent
    data_folder = repo_folder / "data"

    parser = argparse.ArgumentParser(
        "test_solutions.py",
        description="Test all the solutions (i.e., Agent subclasses) to AIRIC GenAI taboo challenge found in a given folder",
    )
    parser.add_argument(
        "--folder",
        default="agents",
        type=str,
        help="The folder where to look for solutions (relative to the repository)",
    )
    parser.add_argument("--levels", type=int, nargs="+", default=[1, 2, 3, 4], help="The Taboo levels to test")
    parser.add_argument(
        "--model-name",
        type=str,
        default="gpt-4o-mini",
        choices=["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"],
        help="The Azure OpenAI model to use to test the solutions",
    )
    parser.add_argument(
        "--quiet", action=argparse.BooleanOptionalAction, default=False, help="Whether to suppress verbose logging"
    )
    parser.add_argument(
        "--words-path",
        type=str,
        default=str(data_folder / "words_with_taboo.txt"),
        help="The path to the file containing words to guess and corresponding taboo words",
    )
    parser.add_argument(
        "--hints-path",
        type=str,
        default=str(data_folder / "level3_data" / "hints.txt"),
        help="The path to the file containing predefined hints for the level 3",
    )
    parser.add_argument(
        "--hints-db-path",
        type=str,
        default=str(data_folder / "level3_data" / "hints_db.json"),
        help="The path to the file containing the precomputed hints vector DB for the level 3",
    )
    parser.add_argument(
        "--translations-path",
        type=str,
        default=str(data_folder / "translations" / "it_fr.json"),
        help="The path to the file containing the translations dict in JSON format for the level 2",
    )

    # Multiprocessing-related parameters
    parser.add_argument(
        "--max-workers",
        type=int,
        default=os.cpu_count(),
        help="The maximum number of processes to use for testing solutions",
    )
    parser.add_argument("--chunksize", type=int, help="The size of the tasks chunk submitted to each worker")

    args = parser.parse_args()

    load_dotenv(dotenv_path=repo_folder / ".env", override=True)

    test_list = [line.split(":") for line in open(args.words_path).read().splitlines()]
    test_list = [
        (guess_word.strip().lower(), [word.strip().lower() for word in taboo_list.split(":")])
        for guess_word, taboo_list in test_list
    ]
    test_hints_level3 = [hint.strip() for hint in open(args.hints_path).read().splitlines()]

    # Load french guesses translations dict
    with open(args.translations_path, "r") as f:
        french_translations_dict = json.load(f)

    with open(args.hints_db_path, "r") as f:
        hints_db = json.load(f)

    use_tqdm = args.quiet
    tasks_parameters = []
    for i, agent_module_path in enumerate(Path(args.folder).iterdir()):
        if not agent_module_path.is_file() or agent_module_path.suffix != ".py":
            continue

        tasks_parameters.append((
            i,
            agent_module_path,
            test_list,
            test_hints_level3,
            french_translations_dict,
            hints_db,
            args.levels,
            not args.quiet,
            args.model_name,
        ))

    processes = min(args.max_workers, len(tasks_parameters))
    chunksize = args.chunksize
    if chunksize is not None:
        chunksize = min(args.chunksize, len(tasks_parameters) // processes + 1)
    with Manager() as manager, Pool(processes=processes, initializer=tqdm.set_lock, initargs=(manager.Lock(),)) as p:
        results = p.map(_test_solution_multiprocessing, tasks_parameters, chunksize=chunksize)

    # Only if tqdm was used, leave some space
    if use_tqdm:
        print("\n" * len(tasks_parameters))

    print(f"\n{'POS':<3} | {'AGENT NAME':<30} | {'TIME':<8} | {'CORRECT':<11} | {'POINTS':<12} | EXCEPTIONS | ACCURACY")
    for i, result in enumerate(
        sorted(results, key=lambda el: el["score"] if isinstance(el, dict) else -1000, reverse=True)
    ):
        if not isinstance(result, dict):
            # An error has occurred, print the agent that had problem and skip the rest
            agent_path, error = result
            print(f"N/A | {str(agent_path):<30} | ERROR: {error}")
            continue

        name, time, raw_results, accuracy, score, exceptions = (
            result["agent_name"],
            result["execution_time"],
            result["raw_results"],
            result["accuracy"],
            result["score"],
            result["exceptions"],
        )
        total_correct = sum(el["correct"] for el in raw_results.values())
        print(
            f"{i + 1:<3} | {name[:30]:<30} | {round(time, 2):<7}s | {total_correct:<3} correct | {score:<5} points | {exceptions:<10} | {accuracy}"
        )


if __name__ == "__main__":
    main()
