from collections import defaultdict
from typing import Tuple
from database import db

_ID_TO_LANGUAGE_NAME = {
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
def get_final_metrics(repo_id: str, commits: Tuple[str]):
    all_metrics_analyzed, present_metrics, analyzed_metrics = db.check_if_metrics_analyzed(repo_id, commits)
    if present_metrics == 0:
        return "Analysis not started yet. Try again in a few seconds. Note: If there will be no results after several" \
               f" attempts, there is a chance that there are no files to analyze for provided commits", 404
    if not all_metrics_analyzed:
        return f"{present_metrics - analyzed_metrics} metrics not fully analyzed yet. Current progress: " \
               f"{analyzed_metrics}/{present_metrics}. Try again in a few seconds.", 404
    return _map_metrics(db.get_metrics(repo_id, commits))


# Always returns metrics, even if not all metrics were analyzed
def get_current_metrics(repo_id: str, commits: Tuple[str]):
    return _map_metrics(db.get_metrics(repo_id, commits))


def _map_metrics(raw_metrics: list) -> dict:
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(defaultdict)))

    for commit_hash, file_path, language_id, h1, h2, n1, n2, vocabulary, length, calculated_length, volume, \
        difficulty, effort, time, bugs, loc, lloc, sloc, comments, multi, blank, single_comments, score, rank, \
        *unrecognized \
            in raw_metrics:
        language_name = _ID_TO_LANGUAGE_NAME[language_id]

        result[commit_hash][file_path][language_name]['h1'] = h1
        result[commit_hash][file_path][language_name]['h2'] = h2
        result[commit_hash][file_path][language_name]['n1'] = n1
        result[commit_hash][file_path][language_name]['n2'] = n2
        result[commit_hash][file_path][language_name]['vocabulary'] = vocabulary
        result[commit_hash][file_path][language_name]['length'] = length
        result[commit_hash][file_path][language_name]['calculated_length'] = calculated_length
        result[commit_hash][file_path][language_name]['volume'] = volume
        result[commit_hash][file_path][language_name]['difficulty'] = difficulty
        result[commit_hash][file_path][language_name]['effort'] = effort
        result[commit_hash][file_path][language_name]['time'] = time
        result[commit_hash][file_path][language_name]['bugs'] = bugs
        result[commit_hash][file_path][language_name]['loc'] = loc
        result[commit_hash][file_path][language_name]['lloc'] = lloc
        result[commit_hash][file_path][language_name]['sloc'] = sloc
        result[commit_hash][file_path][language_name]['comments'] = comments
        result[commit_hash][file_path][language_name]['multi'] = multi
        result[commit_hash][file_path][language_name]['blank'] = blank
        result[commit_hash][file_path][language_name]['single_comments'] = single_comments
        result[commit_hash][file_path][language_name]['score'] = score
        result[commit_hash][file_path][language_name]['rank'] = rank
        if unrecognized:
            result[commit_hash][file_path][language_name]['unrecognized_metrics'] = unrecognized

    return result
