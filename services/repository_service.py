from clients import github
from database import db


def get_repository(repository_name: str):
    # if "github" in url:
    #     return github.get_repository(repository_name)
    # elif "gitlab" in url:
    #     return {
    #         'languages': {},
    #         'branches': [],
    #         'repositoryStatistics': {}
    #     }
    print(f"Metrics analyzed: {db.get_metrics('frege-extractor', 'master')}")
    print(f"Metrics analyzed: {db.check_if_metrics_analyzed('frege-extractor', 'master')}")
    repository_info = github.get_repository(repository_name)

    return repository_info
