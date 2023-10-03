from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metrics.sqlite3'
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

METRICS = [
    'просмотр',
    'время чтения',
    'клик на кнопку навигации',
    'время редактирования',
    'время загрузки страницы',
    'общее количество заметок',
    'среднее количество заметок на пользователе',
    'количество публичных заметок',
    'количество приватных заметок'
]


class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, nullable=False)  # id анализируемой заметки
    event_type = db.Column(db.String(255), nullable=False)  # просмотр, время чтения, клик на кнопку, время редактирования и тд
    event_info = db.Column(db.Text)  # конкретная информация о событии(время чтения, время загрузки и тд)


def save_metric(note_id, event_type, additional_info):
    metric = Metric(note_id=note_id, event_type=event_type, additional_info=additional_info)
    db.session.add(metric)
    db.session.commit()


@app.route('/api/metrics/add', methods=['POST'])
def add_metric():
    data = request.get_json()
    note_id = data.get('note_id')
    event_type = data.get('event_type')
    event_info = data.get('event_info')

    if note_id is None or event_type is None or event_info is None:
        return jsonify({'error': 'Missing parameters'}), 400
    elif event_type not in METRICS:
        return jsonify({'error': 'Wrong event_type'}), 400

    save_metric(note_id, event_type, event_info)
    return jsonify({'message': 'Metric added successfully'}), 201


@app.route('/api/metrics/view', methods=['GET'])
def get_view_metrics():
    event_type = request.args.get('event_type')  # event_type='просмотр', если GET-запрос был по ссылке /api/metrics/view?event_type=просмотр
    if event_type is None:
        return jsonify({'error': 'Missing event_type parameter'}), 400
    metrics = Metric.query.filter_by(event_type=event_type).all()
    view_metrics = []
    for metric in metrics:
        view_metric = {
            'note_id': metric.note_id,
            'event_type': metric.event_type,
            'event_info': metric.event_info
        }
        view_metrics.append(view_metric)
    return jsonify({'view_metrics': view_metrics})


if __name__ == '__main__':
    db.create_all()
    app.run()
