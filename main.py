import os

from flask import Flask, request
from services.metrics_service import get_final_metrics, get_current_metrics, ID_TO_LANGUAGE_NAME
from services.repository_service import get_repository

app = Flask(__name__)


@app.route("/repository")
def repository():
    return get_repository(repo_id=request.args['repo_id'])


@app.route("/metrics", methods=["POST"])
def all_metrics():
    if request.headers.get('Content-Type') != 'application/json':
        return 'Content-Type not supported!', 415

    request_body = request.json
    repo_id, commits = request_body['repo_id'], tuple(request_body['commits'])
    languages = tuple(request_body.get('languages', ID_TO_LANGUAGE_NAME.keys()))
    return_only_if_all_available = request_body.get('return_only_if_all_available', False)

    if return_only_if_all_available:
        return get_final_metrics(repo_id, commits, languages)
    else:
        return get_current_metrics(repo_id, commits, languages)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 8080)))
