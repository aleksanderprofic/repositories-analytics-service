import psycopg2

from config import DB_HOST, DB_NAME, DB_PORT, DB_PASS, DB_USER

query_metrics = """SELECT commit_hash, language_id, file_path, h1, h2, n1, 
            n2, vocabulary, length, calculated_length, volume, difficulty, effort, time, bugs, loc, lloc, sloc, 
            comments, multi, blank, single_comments, score, rank
                    FROM python_file_halstead_metrics hm
                        JOIN python_file_loc_metrics lm ON hm.python_file_id=lm.python_file_id
                        JOIN python_file_mi_metrics mm ON hm.python_file_id=mm.python_file_id
                        JOIN python_file pf ON hm.python_file_id = pf.id
                        JOIN repository_language_file rlf on pf.file_id = rlf.id
                        JOIN repository_language rl on rlf.repository_language_id = rl.id
                        WHERE repository_id=%s AND commit_hash=%s"""

query_metrics_analyzed = """SELECT COUNT(*) FROM repository_language rl
                        WHERE repository_id=%s AND commit_hash=%s AND present=true AND analyzed=true"""

query_metrics_present = """SELECT COUNT(*) FROM repository_language rl
                        WHERE repository_id=%s AND commit_hash=%s AND present=true"""


def _connect():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)


def get_metrics(repo_id: str, commit_hash: str):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_metrics, [repo_id, commit_hash])
            return cur.fetchall()


def check_if_metrics_analyzed(repo_id: str, commit_hash: str) -> bool:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_metrics_present, [repo_id, commit_hash])
            present = cur.fetchone()[0]
            if present == 0:
                return False

            cur.execute(query_metrics_analyzed, [repo_id, commit_hash])
            analyzed = cur.fetchone()[0]

            return present - analyzed == 0
