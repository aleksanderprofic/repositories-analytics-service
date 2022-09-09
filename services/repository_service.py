from clients import github


def get_repository(repository_name: str):
    # if "github" in url:
    #     return github.get_repository(repository_name)
    # elif "gitlab" in url:
    #     return {
    #         'languages': {},
    #         'branches': [],
    #         'repositoryStatistics': {}
    #     }
    return github.get_repository(repository_name)
