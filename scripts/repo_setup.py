#!/usr/bin/python3

from pathlib import Path
import subprocess
import argparse
from urllib.request import urlopen
from urllib.error import HTTPError
import zipfile
from tempfile import TemporaryFile, TemporaryDirectory
import shutil
import platform

REPO_HTTPS_URL = "https://github.com/AIRIC-Polimi/taboo4students.git"
REPO_SSH_URL = "git@github.com:AIRIC-Polimi/taboo4students.git"
REPO_ZIP_URL = "https://github.com/AIRIC-Polimi/taboo4students/archive/refs/heads/main.zip"


def download_and_unzip(output_directory: str):
    # Download the ZIP file
    with urlopen(REPO_ZIP_URL) as response:
        if response.status != 200:
            print(REPO_ZIP_URL)
            raise HTTPError(
                REPO_ZIP_URL,
                response.status,
                f"Unexpected {response.status} error while downloading ZIP file",
                response.headers,
                None,
            )

        # Write the response to a temporary file, from which we can unzip
        with TemporaryFile() as tmp_file:
            tmp_file.write(response.read())

            # Unzip to a temporary directory than move the only subfolder (which is the actual repo folder) to the target output directory
            with zipfile.ZipFile(tmp_file, "r") as zip_file, TemporaryDirectory() as tmp_dir:
                zip_file.extractall(tmp_dir)
                repo_subfolder = next(Path(tmp_dir).iterdir())
                shutil.move(repo_subfolder, output_directory)


def clone_repo(output_directory: str, use_ssh: bool = False) -> Path:
    current_folder = Path.cwd()

    print("[SETUP]\tCloning the repository")
    try:
        result = subprocess.run(["git", "-h"], capture_output=True)
        assert result.returncode == 0
        use_git = True
    except:
        print("[SETUP]\tgit not found, falling over to raw ZIP download")
        use_git = False

    if output_directory is None:
        repo_folder = input(f"Where do you want to clone the repository (default: {current_folder})? ")
        if repo_folder is None:
            repo_folder = current_folder
    else:
        repo_folder = output_directory
    repo_folder = Path(repo_folder).absolute()

    if repo_folder.exists() and repo_folder.is_dir():
        repo_folder = repo_folder / "taboo"
    if repo_folder.exists():
        raise ValueError(f"Unable to clone repo into folder {repo_folder}, which is already existing")

    if use_git:
        subprocess.run(["git", "clone", REPO_SSH_URL if use_ssh else REPO_HTTPS_URL, repo_folder])
    else:
        download_and_unzip(output_directory=repo_folder)

    return repo_folder


def main():
    parser = argparse.ArgumentParser(
        "repo_setup.py", description="Clone and setup the repository for the AIRIC GenAI taboo challenge"
    )
    parser.add_argument("--output", "-o", help="The folder where to clone and setup the repository")
    parser.add_argument("--api-key", help="The Azure OpenAI API KEY provided by the organizers")
    parser.add_argument(
        "--git-ssh",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to use SSH to clone the git repo",
    )

    args = parser.parse_args()

    # Check if the script is run from a remote location (or if it has been downloaded, e.g. via a git clone, and then run),
    # and if the script has been run from a downloaded copy of the entire repo (as opposed to having been downloaded, saved and run)
    is_script_run_remotely = not Path(__file__).is_file()
    is_script_in_repo = (Path(__file__).parent.parent / ".gitignore").is_file()

    # Clone the repository (if needed)
    if is_script_run_remotely or not is_script_in_repo:
        repo_folder = clone_repo(output_directory=args.output, use_ssh=args.git_ssh)
    else:
        repo_folder = Path(__file__).parent.parent

    # Create the virtual environment
    print("[SETUP]\tCreating the python virtual environment")
    venv_folder = repo_folder / ".venv-taboo"
    subprocess.run(["python3", "-m", "venv", venv_folder])

    # Install the dependencies
    print("[SETUP]\tInstalling the dependencies")
    if platform.system().lower() == "windows":
        subprocess.run([venv_folder / "Scripts" / "pip.exe", "install", "-e", repo_folder])
    else:
        subprocess.run([venv_folder / "bin" / "pip", "install", "-e", repo_folder])

    # Configure the .env file
    print("[SETUP]\tConfiguring the .env file")
    with open(repo_folder / ".env.example", "r") as f:
        env_file = f.read()
    path_db = repo_folder / "level3_data" / "hints_db.json"
    path_hints = repo_folder / "level3_data" / "hints.txt"
    path_words = repo_folder / "words_with_taboo.txt"
    env_file = (
        env_file.replace("path_to_db", str(path_db))
        .replace("path_to_hints", str(path_hints))
        .replace("path_to_taboo_words", str(path_words))
    )
    if args.api_key is None:
        api_key = input("Please insert the Azure OpenAI API KEY given by the organizers: ")
    else:
        api_key = args.api_key
    env_file = env_file.replace("your_key_here", api_key)
    with open(repo_folder / ".env", "w") as f:
        f.write(env_file)


if __name__ == "__main__":
    main()
