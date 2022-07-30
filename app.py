from crypt import methods
from flask import Flask, request, render_template, url_for
from flask_restx import Api, Resource

from pathlib import Path

UPLOAD_FOLDER = Path(__file__).parent
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
api = Api(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', 
                           collect_data_route=url_for('collect_data'))


@api.route('/collect-data', methods=['POST'])
@api.route('/check/<str:task_id>', methods=['GET'])
class ProcessInnsRoute(Resource):

    def post():
        file = request.files.get('inns')
        return file.filename if file else 'Ничего не получено'

    def get(task_id):
        pass

@app.route('/download/<str:task_id>')
def download(task_id):
    pass

if __name__ == '__main__':
    pass