from flask import Flask, render_template
from flask_restx import Api

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    pass


@api.route('/collect-data', methods=('POST', ))
def collect_data():
    pass


@api.route('/check/<str:task_id>')
def check_status(task_id):
    pass


@api.route('/download/<str:task_id>')
def download(task_id):
    pass

if __name__ == '__main__':
    app.run(debug=True)