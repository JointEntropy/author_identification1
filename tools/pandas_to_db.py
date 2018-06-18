import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from init_db import db_create
from predict_models.utils import filter_by_samples_count

# connection = engine.raw_connection()
# data_path = '/media/grigory/Data/DIPLOM_DATA/dataset_with_names.csv'
data_path = '/media/grigory/Диск/DIPLOM_DATA/loveread_fantasy_dataset_0.csv'

# db_path = 'sqlite:///../data/test.db'
db_path  = 'sqlite:////media/grigory/Диск/DIPLOM_DATA/db/loveread_wordlstm_fantasy_0.db'


def save_dataframe(engine, df, table):
    df.to_sql(con=engine, index='id', name=table, if_exists='append')
    # with engine.connect() as con:
    #     con.execute('ALTER TABLE {table} ADD PRIMARY KEY {key}'.format(table=table, key='id'))


def read_table(engine, table):
    return pd.read_sql_table(table, engine)


def prepare_author_table(data):
    unique_authors = data['author'].value_counts().index.values
    mapping = dict(((name, idx) for idx, name in enumerate(unique_authors)))

    df = pd.DataFrame({'name': unique_authors},
                      columns=['name', 'bio', 'img_url'])
    return df, mapping


def prepare_text_table(data, mapping, generate_title=False):
    if generate_title:
        titles = data['text'].apply(lambda x: ''.join(x[:30])).values
    else:
        titles = data['name'].fillna('..').values

    text_df = pd.DataFrame({
        'text': data['text'].values,
        'author_id':  data['author'].apply(lambda x: mapping[x]).values,
        'title': titles,

    }, columns=['title', 'text', 'author_id', 'features'])
    return text_df


if __name__ == '__main__':
    # создание базы
    db_create()

    # инициализация
    engine = create_engine(db_path)
    Base = declarative_base()
    Base.metadata.create_all(engine)

    df = pd.read_csv(data_path)

    # Фильтруем так как при обучении

    # выбираем топ 300 авторов
    authors_count_limit = 300
    top_authors = set(df['author'].value_counts()[:authors_count_limit].index.values)
    mask = df['author'].apply(lambda x: x in top_authors)
    df = df[mask]

    # по минимальному числу фрагментов
    samples_count_lower = 50
    df = filter_by_samples_count(df, samples_count_lower)

    # assert df.index.value_counts().values.max() == 1

    ## Готовим таблицу с авторами
    author_df, authors_mapping = prepare_author_table(df)
    save_dataframe(engine, author_df, 'author')

    # Готовим таблицу с произведениями
    text_df = prepare_text_table(df, authors_mapping, generate_title=True)
    save_dataframe(engine, text_df, 'composition')

    # проверяем результат
    # author_df = read_table(engine, 'Composition')
    # comp_df = read_table(engine, 'Composition')