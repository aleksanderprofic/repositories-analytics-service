from clients import github


def get_repository(repository_name: str):
    # In the future: add logic to decide which provider to use (GitHub, Gitlab, Bitbucket etc.)
    return github.get_repository(repository_name)
