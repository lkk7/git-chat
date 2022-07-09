import argparse
import logging as log
import os


from git_chat.client import ChatClient

log.basicConfig(level=log.INFO, format="%(levelname)s: %(message)s")


def directory_arg(path: str) -> str:
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")


def main() -> None:
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository", help="path to the chat repository", type=directory_arg
    )
    args = parser.parse_args()

    try:
        chat_client = ChatClient(args.repository)
        chat_client.run()
    except (KeyboardInterrupt, EOFError):
        log.warning("Keyboard interrupt or error: quitting")


if __name__ == "__main__":
    main()
