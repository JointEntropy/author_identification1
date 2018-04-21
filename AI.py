import os
import glob
from flask import Flask, request, render_template,   Response, abort
from flask import Flask, flash, request, redirect, url_for, render_template,  send_file
from scikit_interface import calculate
from werkzeug.utils import secure_filename
import json


# def parse_methods(dirname):
#     methods = {}
#     for descr_file in glob.glob(os.path.join(dirname, '*.json')):
#         name = (descr_file.rsplit(os.path.sep, maxsplit=1)[1]).split('.')[0]
#         methods[name] = open(descr_file, 'r').read()
#     return methods
#
# METHODS_AND_PARAMS = parse_methods(dirname='methods')


ALLOWED_EXTENSIONS = set(['json'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = 'Master Kenobi!'


@app.route('/', methods=['GET'])
def debug_page():
    """
    Отрисовка страницы ручной отправки данных.
    :return: страница ручной отправки данных.
    """
    return render_template('main.html')


@app.route('/submit', methods=['POST'])
def submit():
    """
    Обработка post запроса на кластеризацию полученных данных.
    :return: список кортежей: метка кластера, входной объект.
    """
    request_data = json.loads(request.data.decode('utf8'))
    # try:
    #     result = calculate(**request_data)
    # except ValueError:
    #     return abort(400)

    result = {"author": "Ленин",
              "prob": 0.93 ,
              "img_url": "https://s11.stc.all.kpcdn.net/share/i/12/10034942/inx960x640.jpg"}
    result = json.dumps(result, indent=3)
    response = Response(result, mimetype='text/json')
    # response.headers['Content-Disposition'] = "inline; filename=" + filename
    return response


@app.route('/methods', methods=['GET'])
def get_methods():
    """
    Получение списка названий доступных методов.
    :return: список названий доступных методов в формате json.
    """
    methods = list(METHODS_AND_PARAMS.keys())
    return Response(json.dumps(methods), mimetype='text/json')


@app.route('/format/<method>')
def method_description(method):
    """
    Получение описания полей для метода.
    :param method: имя метода для которого требуется получить описание.
    :return: словарь с описания полей  в формате json и ссылка для результата.
    """
    if method in METHODS_AND_PARAMS:
        response = {
            'submit_url': '/submit',
            'fields': json.loads(METHODS_AND_PARAMS[method])
        }
        return Response(json.dumps(response), mimetype='text/json')
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
    app.run()

