import logging as log
from typing import Final, List, Optional

import pygit2


INIT_COMMIT_MSG: Final[str] = "!init"


def print_message(commit: pygit2.Commit) -> None:
    """Print a commit message in a chat-like format."""
    print(f"[{commit.author}]({commit.short_id}): {commit.message.rstrip()}")


class ChatClient:
    def __init__(self, repo_path: str) -> None:
        """Load the repository, git-checkout the branch, verify their correctness."""
        self.repo_path = repo_path
        self.repo: Optional[pygit2.Repository] = None
        self.branch: Optional[str] = None
        self.latest_commit_id: Optional[pygit2.Oid] = None

        try:
            self.repo = pygit2.Repository(repo_path)
            log.info("Successfully loaded a chat repository at %s", repo_path)
        except pygit2.GitError:
            log.critical("Could not find any repository at %s", repo_path)
            return
        try:
            init_commit_msg = self.get_commit_list()[-1].message.rstrip()
            if init_commit_msg != INIT_COMMIT_MSG:
                raise RuntimeError
        except (pygit2.GitError, RuntimeError):
            log.critical(
                "Could not find a corrent initial commit "
                '(first commit should contain "!init")'
            )
            # Invalidate the repository to prevent run().
            self.repo = None
            return

    def get_commit_list(self) -> List[pygit2.Commit]:
        """Get the full list of commits in the current repository."""
        if not self.repo:
            log.critical("Cannot run when unitialized, quitting")
            return []
        return list(
            self.repo.walk(self.repo[self.repo.head.target].id, pygit2.GIT_SORT_TIME)
        )

    def send_message(self, message: str) -> pygit2.Oid | None:
        """Send out the message, i.e. create an empty commit with that message

        Returns: ID of the created commit.
        """
        if not self.repo:
            log.critical("Cannot run when unitialized, quitting")
            return None
        commit_parents = [self.repo.head.target]
        ref = self.repo.head.name
        index = self.repo.index
        signature = self.repo.default_signature

        index.add_all()
        index.write()
        tree = index.write_tree()
        return self.repo.create_commit(
            ref,
            signature,
            signature,
            message,
            tree,
            commit_parents,
        )

    def run(self) -> None:
        """Run the main loop of the client."""
        if not self.repo:
            log.critical("Cannot run when unitialized, quitting")
            return
        for commit in reversed(self.get_commit_list()[:-1]):
            print_message(commit)
        self.latest_commit_id = self.repo[self.repo.head.target].id
        while True:
            try:
                message = input(">>> ")
            except EOFError:
                log.warning("Keyboard interrupt or error, quitting")
                return

            new_commits: List[pygit2.Object] = []
            latest_commit = self.repo[self.repo.head.target]
            tmp_commit = latest_commit
            while self.latest_commit_id != latest_commit.id:
                new_commits.append(latest_commit)
                if len(latest_commit.parents) == 0:
                    break
                latest_commit = self.repo[latest_commit.parents[0].id]
            self.latest_commit_id = tmp_commit.id
            for commit in reversed(new_commits):
                print_message(commit)
            if message:
                self.latest_commit_id = self.send_message(message)
                print_message(self.repo[self.latest_commit_id])
