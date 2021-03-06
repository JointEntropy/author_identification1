from flask import Response, abort
from flask import request, render_template
import json
from sqlalchemy.orm import load_only
from gvars import app
from backend import be, Author, Composition
from flask import flash
from flask import redirect


@app.route('/', methods=['GET'])
def debug_page():
    """
    Отрисовка страницы ручной отправки данных.
    :return: страница ручной отправки данных.
    """
    return render_template('main.html')


@app.route('/analyze_quality', methods=['POST'])
def analyze_quality():
    text = request.form.get('text', None)
    if text:
        # result = be.analyze_quality()
        result = {
            'acc': 0.99,
        }
        result = json.dumps(result, indent=3)
        return Response(result, mimetype='text/json')
    else:
        return abort(400)


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


@app.route('/delete', methods=['POST'])
def delete():
    entity_name = request.form.get('entity_name', None)
    idx = request.form.get('id', None)
    if entity_name == 'author':
        be.del_author(idx)
    elif entity_name == 'composition':
        be.del_comp(idx)
    return  json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/add_comp', methods=['POST'])
def add_composition():
    try:
        request_data = json.loads(request.data.decode('utf8'))
        composition = {
            'author_name': request_data['author_name'],
            'text': request_data['text'],
            'title':  request_data['title']
        }
        if any(not bool(val) for key, val in composition.items()):
            raise ValueError
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
    result = json.dumps(result, indent=3)
    response = Response(result, mimetype='text/json')
    return response


@app.route('/comp/<comp_id>')
def composition(comp_id):
    # flash('О май гад')
    # return redirect('index/composition/1')
    composition = be.get_composition(comp_id)
    return render_template('text_view.html', editable=True, entity_name='author', **composition)


@app.route('/index/<entity_name>/<page_id>')
def index(entity_name, page_id):
    filter_col = request.args.get('filter_col', None)
    filter_idx = request.args.get('filter_idx', None)
    search_str = request.args.get('search_str', None)
    page_id = int(page_id)

    if str(search_str) != 'None':
        if entity_name == 'composition':
            q = Composition.query.filter(Composition.title.contains(search_str))\
                .options(load_only('id', 'title','author_id'))
            header = 'Поиск среди произведений по запросу "{}"'.format(search_str)
        elif entity_name == 'author':
            q = Author.query.filter(Author.name.contains(search_str)).options(load_only('id', 'name'))
            header = 'Поиск среди авторов по запросу "{}"'.format(search_str)
    else:
        if entity_name == 'author' and str(filter_col) == 'None':
            q = Author.query.options(load_only('name', 'id'))
            header = 'Авторы'
        elif entity_name == 'composition' and filter_col == 'author':
            q = Composition.query.filter_by(author_id=filter_idx).options(load_only('title', 'author_id', 'id'))
            header = Author.query.get(filter_idx).name
        elif entity_name == 'composition':
            q = Composition.query.options(load_only('title', 'author_id', 'id'))
            header = 'Произведения'
    paginator = q.paginate(page_id, app.config['MAX_ITEMS_PER_PAGE'], False)
    entities = paginator.items
    return render_template('index.html', header=header,
                           entity_name=entity_name,
                           entities=entities,
                           page_id=page_id,
                           pages=paginator.pages,
                           filter_col=filter_col,
                           filter_idx=filter_idx,
                           search_str=search_str)


@app.route('/author/<author_id>')
def author_info(author_id):
    author = be.get_author_info(author_id)
    if author is not None:
        return Response(json.dumps(author), mimetype='text/json')
    else:
        return abort(400)


@app.route('/edit_field/<entity_name>/<idx>', methods=['POST'])
def edit_field(entity_name, idx):

    field_name = request.form.get('field')
    field_value = request.form.get('value')
    if entity_name == 'authors':
        be.edit_author(idx, {
            field_name:  field_value
        })
    elif entity_name == 'comps':
        be.edit_composition(idx,{
            field_name: field_value
        })
    return  json.dumps({'success':True}), 200, {'ContentType':'application/json'}


# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if user does not select file, browser also submit a empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             # Сохраняем файл в директории
#             file.save(os.path.join(app.instance_path, filename))#app.config['UPLOAD_FOLDER'], filename))
#
#             # Перенаправляем пользователя, как только так сразу.
#             # url = url_for('uploaded_file', filename=result_path)  # первый аргумент url_for -  название контроллера.
#             # return url
#         else:
#             flash('Invalid extension of selected file')
#             return redirect(request.url)
#     return render_template('upload_page.html', methods_and_params=METHODS_AND_PARAMS)
