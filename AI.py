from gvars import app
from flask_sqlalchemy import SQLAlchemy
import os
from flask import   Response, abort
from flask import  flash, request, redirect, url_for, render_template,  send_file
from werkzeug.utils import secure_filename
import json
from backend import MBackEnd
from tools.file_filter import allowed_file
from models import User, Author, Composition
from sqlalchemy.orm import load_only
from tools.decoders import  Decoder
from predict_models import BWordCharLSTM, WordLSTM, PredictModel
from gvars import modal_package_path

from tools.init_db import  restore_after_flush


@app.route('/', methods=['GET'])
def debug_page():
    """
    Отрисовка страницы ручной отправки данных.
    :return: страница ручной отправки данных.
    """
    return render_template('main.html')


@app.route('/authors', methods=['GET'])
def get_authors():
    """
    Отрисовка страницы ручной отправки данных.
    :return: страница ручной отправки данных.
    """
    result = be.get_authors()
    result = json.dumps(result, indent=3)
    response = Response(result, mimetype='text/json')
    return response


@app.route('/add_comp', methods=['POST'])
def add_composition():
    try:
        request_data = json.loads(request.data.decode('utf8'))
        composition = {
            'author_name': request_data['author_name'],
            'text': request_data['text'],
            'title':  request_data['text']
        }
        be.add_composition(composition)
    except ValueError:
        return abort(400)

    result = json.dumps({}, indent=3)
    response = Response(result, mimetype='text/json')
    # response.headers['Content-Disposition'] = "inline; filename=" + filename
    return response

@app.route('/submit', methods=['POST'])
def submit():
    try:
        request_data = json.loads(request.data.decode('utf8'))
        text = request_data['text']
        result = be.predict(text)
    except ValueError:
        return abort(400)

    result = {"author": "Ленин",
              "prob": 0.93 ,
              "img_url": "https://s11.stc.all.kpcdn.net/share/i/12/10034942/inx960x640.jpg"}
    result = json.dumps(result, indent=3)
    response = Response(result, mimetype='text/json')
    # response.headers['Content-Disposition'] = "inline; filename=" + filename
    return response


@app.route('/comp/<comp_id>')
def composition(comp_id):
    composition = be.get_composition(comp_id)
    return render_template('text_view.html', editable=True, entity_name='author', **composition)


@app.route('/index/<entity_name>/<page_id>')
def index(entity_name, page_id):
    filter_col = request.args.get('filter_col', None)
    filter_idx = request.args.get('filter_idx', None)
    MAX_ITEMS_PER_PAGE = 15
    page_id = int(page_id)

    if entity_name == 'author' and str(filter_col) == 'None':
        paginator = Author.query.options(load_only('name', 'id')).paginate(page_id, MAX_ITEMS_PER_PAGE, False)
        entities = paginator.items
        header='Авторы'

    elif entity_name == 'composition' and filter_col == 'author':
        paginator = Composition.query.filter_by(author_id=filter_idx).\
            options(load_only('title', 'author_id', 'id')).paginate(page_id, MAX_ITEMS_PER_PAGE, False)
        entities = paginator.items
        header = Author.query.get(filter_idx).name
    elif entity_name == 'composition':
        paginator = Composition.query.options(load_only('title', 'author_id', 'id')).paginate(page_id,
                                                                      MAX_ITEMS_PER_PAGE, False)
        entities = paginator.items
        header='Произведения'
    return render_template('index.html', header=header, entity_name=entity_name,
                           entities=entities,
                           page_id=page_id,
                           pages=paginator.pages, # pages stands for max_pages
                           filter_col=filter_col,
                           filter_idx=filter_idx)


@app.route('/author/<author_id>')
def author_info(author_id):
    author = be.get_author_info(author_id)
    if author is not None:
        return Response(json.dumps(author), mimetype='text/json')
    else:
        return abort(400)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Сохраняем файл в директории
            file.save(os.path.join(app.instance_path, filename))#app.config['UPLOAD_FOLDER'], filename))

            # Перенаправляем пользователя, как только так сразу.
            # url = url_for('uploaded_file', filename=result_path)  # первый аргумент url_for -  название контроллера.
            # return url
        else:
            flash('Invalid extension of selected file')
            return redirect(request.url)
    return render_template('upload_page.html', methods_and_params=METHODS_AND_PARAMS)


if __name__ == '__main__':
    restore_after_flush()

    db = SQLAlchemy()
    decoder = Decoder(None)
    inner_model = WordLSTM(modal_package_path) #BWordCharLSTM(modal_package_path)
    model = PredictModel(inner_model)
    be = MBackEnd(model, db, decoder)

    # app.config['DEBUG'] = True
    # сейчас app импортится из вьюхи...
    app.run(host='0.0.0.0')

