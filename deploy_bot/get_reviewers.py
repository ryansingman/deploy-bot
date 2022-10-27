import re
import subprocess
from typing import List


def find_contributors_to_branch(base_branch: str, target_branch: str) -> List[str]:
    """Finds authors of commits to base branch that are NOT in target branch.

    :param base_branch: base branch of diff
    :param target_branch: target branch of diff
    :return: list of authors of commits in base branch but not in target
    """
    commit_hashes: List[str] = find_added_commits(base_branch=base_branch, target_branch=target_branch)

    return [find_author_of_commit(commit_hash) for commit_hash in commit_hashes]


def find_author_of_commit(commit_hash: str) -> str:
    """Finds author of commit.

    :param commit_hash: commit hash to find author for
    :return: author of commit hash
    """
    # run `git log` to find author
    command_output: subprocess.CompletedProcess = subprocess.run(
        ["git", "log", commit_hash, "-1", "--format='%an'"],
        capture_output=True,
        check=True,
    )

    # parse author from command output
    return command_output.stdout.decode().splitlines()[0][1:-1]


def find_added_commits(base_branch: str, target_branch: str) -> List[str]:
    """Finds commits to base branch that are NOT in target branch.

    :param base_branch: base branch of diff
    :param target_branch: target branch of diff
    :return: commit hashes in base branch that are NOT in target
    """
    # run `git cherry` to find commits
    command_output: subprocess.CompletedProcess = subprocess.run(
        ["git", "cherry", target_branch, base_branch],
        capture_output=True,
        check=True,
    )

    # parse and return commit hashes from command output
    return [
        get_commit_hash_from_git_cherry_line(line)
        for line in command_output.stdout.decode().splitlines()
        if is_added_commit(line)
    ]


def get_commit_hash_from_git_cherry_line(line: str) -> str:
    """Parses git cherry line into commit hash.

    :param line: line from git cherry output to parse
    :return: commit hash
    """
    try:
        return re.search(r"\b([0-9a-f]{5,40})\b", line).group(1)
    except AttributeError:
        raise RuntimeError("Could not parse commit hash from git cherry -- aborting.")


def is_added_commit(line: str) -> bool:
    """Returns true if line is of an added commit (starts with '+').

    :param line: line to determine if is an addition
    :return: true if line is an addition
    """
    return line.startswith("+")


if __name__ == "__main__":

    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="Get reviewers for PR")
    parser.add_argument(
        "--base-branch",
        dest="base_branch",
        help="base branch for comparison",
    )
    parser.add_argument(
        "--target-branch",
        dest="target_branch",
        help="target branch for comparison",
    )

    args = parser.parse_args()

    # find contributors to branch
    contributors: List[str] = find_contributors_to_branch(args.base_branch, args.target_branch)

    # output contributors as comma delimited list
    print(",".join(contributors))

    exit(0)
