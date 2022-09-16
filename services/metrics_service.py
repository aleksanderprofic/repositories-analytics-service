from collections import defaultdict
from typing import Tuple

from database import db

ID_TO_LANGUAGE_NAME = {
    1: 'C',
    2: 'C++',
    3: 'C#',
    4: 'CSS',
    5: 'Java',
    6: 'JS',
    7: 'PHP',
    8: 'Python',
    9: 'Ruby',
}


# Returns metrics only when all were analyzed, otherwise returns 404
def get_final_metrics(repo_id: str, commits: Tuple[str], languages: Tuple[int]):
    all_metrics_analyzed, present_metrics, analyzed_metrics = db.check_if_metrics_analyzed(repo_id, commits)
    if present_metrics == 0:
        download_time = db.check_repo_download_time(repo_id)
        if not download_time:
            # TODO: Send message to queue - initiate analysis
            return "Analysis initiated", 201
        return "Analysis just started. Try again in a few seconds. Note: If there will be no results after several" \
               f" attempts, there is a chance that there are no files to analyze for provided commits", 404
    if not all_metrics_analyzed:
        return f"{present_metrics - analyzed_metrics} metrics not fully analyzed yet. Current progress: " \
               f"{analyzed_metrics}/{present_metrics}. Try again in a few seconds.", 404
    return _map_metrics(db.get_metrics(repo_id, commits, languages))


# Always returns metrics, even if not all metrics were analyzed
def get_current_metrics(repo_id: str, commits: Tuple[str], languages: Tuple[int]):
    return _map_metrics(db.get_metrics(repo_id, commits, languages))


def _map_metrics(raw_metrics: list) -> dict:
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(defaultdict)))

    for commit_hash, file_path, language_id, h1, h2, n1, n2, vocabulary, length, calculated_length, volume, \
        difficulty, effort, time, bugs, loc, lloc, sloc, comments, multi, blank, single_comments, score, rank, \
        *unrecognized \
            in raw_metrics:
        language_name = ID_TO_LANGUAGE_NAME[language_id]

        result[commit_hash][language_name][file_path]['h1'] = h1
        result[commit_hash][language_name][file_path]['h2'] = h2
        result[commit_hash][language_name][file_path]['n1'] = n1
        result[commit_hash][language_name][file_path]['n2'] = n2
        result[commit_hash][language_name][file_path]['vocabulary'] = vocabulary
        result[commit_hash][language_name][file_path]['length'] = length
        result[commit_hash][language_name][file_path]['calculated_length'] = calculated_length
        result[commit_hash][language_name][file_path]['volume'] = volume
        result[commit_hash][language_name][file_path]['difficulty'] = difficulty
        result[commit_hash][language_name][file_path]['effort'] = effort
        result[commit_hash][language_name][file_path]['time'] = time
        result[commit_hash][language_name][file_path]['bugs'] = bugs
        result[commit_hash][language_name][file_path]['loc'] = loc
        result[commit_hash][language_name][file_path]['lloc'] = lloc
        result[commit_hash][language_name][file_path]['sloc'] = sloc
        result[commit_hash][language_name][file_path]['comments'] = comments
        result[commit_hash][language_name][file_path]['multi'] = multi
        result[commit_hash][language_name][file_path]['blank'] = blank
        result[commit_hash][language_name][file_path]['single_comments'] = single_comments
        result[commit_hash][language_name][file_path]['score'] = score
        result[commit_hash][language_name][file_path]['rank'] = rank
        if unrecognized:
            result[commit_hash][language_name][file_path]['unrecognized_metrics'] = unrecognized

    return result
