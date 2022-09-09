import os

from flask import Flask, request

from services.repository_service import get_repository

app = Flask(__name__)


@app.route("/repository")
def repository():
    return get_repository(repository_name=request.args['repositoryName'])


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 8080)))
