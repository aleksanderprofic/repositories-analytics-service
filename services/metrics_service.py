from collections import defaultdict
from typing import Tuple

import json
import logging
import pika
import time
from config import OUT_QUEUE_NAME, RABBITMQ_HOST, RABBITMQ_PORT, PUBLISH_DELAY


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


def _send_message(message, queue, _output_channel):
    """Send output message to queues specified by name"""
    while True:
        # List of queues to retry sending
        retry = False
        try:
            logging.info(f"Sending message to {queue}...")
            _output_channel.basic_publish(
                exchange='',
                routing_key=queue,
                properties=pika.BasicProperties(delivery_mode=2, ),
                body=bytes(json.dumps(message), encoding='utf8')
            )
            logging.info("Output message received by RabbitMQ")
        except pika.exceptions.NackError as e:
            logging.info(f"Output message NACK from RabbitMQ (queue full)."
                         f" Retrying in {PUBLISH_DELAY} s")
            retry = True
        # If the queues to retry list is not empty
        if retry:
            time.sleep(PUBLISH_DELAY)
        else:
            break


def get_metrics(repo_id: str, commits: Tuple[str], languages: Tuple[int], get_currently_available: bool):
    if not db.check_repo_download_time(repo_id):
        analyzed_commits = db.get_analyzed_commits(repo_id, languages)

        commits_to_analyze = set(commits).difference(analyzed_commits)

        message_to_queue = {'repo_id': repo_id, 'languages': languages, 'commits': commits_to_analyze}

        with pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)) as connection:
            _output_channel = connection.channel()
            _output_channel.confirm_delivery()
            _output_channel.queue_declare(queue=OUT_QUEUE_NAME, durable=True)
            logging.info("Connected.")

            _send_message(message_to_queue, OUT_QUEUE_NAME, _output_channel)
            logging.info("Finished extractor task.\n")

    if not get_currently_available:
        all_metrics_analyzed, present_metrics, analyzed_metrics = db.get_metrics_analysis_info(repo_id, commits)
        if present_metrics == 0:
            return "Analysis just started. Try again in a few seconds. Note: If there will be no results after several" \
                   f" attempts, there is a chance that there are no files to analyze for provided commits", 404
        if not all_metrics_analyzed:
            return f"{present_metrics - analyzed_metrics} metrics not fully analyzed yet. Current progress: " \
                   f"{analyzed_metrics}/{present_metrics}. Try again in a few seconds.", 404

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
