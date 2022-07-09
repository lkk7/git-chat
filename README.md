# git-chat

A chat client that can use git repositories as servers.\
This is just a proof of concept, so it's limited to local repos and doesn't poll for changes efficiently.\
**This is not usable in any context and makes no sense, it's just for fun!**

## Installation & usage

For a quick install, poetry is required:

```sh
poetry install
```

Then, create a git repository somewhere.\
To prevent touching some repository by accident, a chat repository has to have an initial commit with a message `!init`.\
You can add it by: `git commit -m '!init' --allow-empty`.

You can test how it works by launching two clients in separate terminals:

```sh
poetry run python git_chat [repository path]
```
