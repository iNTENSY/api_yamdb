from django.core.management.base import BaseCommand

import os
import csv
import sqlite3

VALID_DATA = {
    'users': {
        'table_name': 'users_user',
        'fieldnames': ['id', 'password', 'last_login', 'is_superuser',
                       'is_staff', 'is_active', 'date_joined', 'username',
                       'email', 'first_name', 'last_name', 'bio', 'role',
                       'confirmation_code'],
        'order': [0, 7, 8, 12, 13, 9, 10, 1, 2, 11, 4, 5, 3, 6]
    },
    'titles': {
        'table_name': 'reviews_title',
        'fieldnames': ['id', 'name', 'year', 'description', 'category_id'],
        'order': [0, 1, 2, 4, 3]
    },
    'comments': {
        'table_name': 'reviews_comment'
    },
    'genre_title': {
        'table_name': 'reviews_title_genre'
    },
    'category': {
        'table_name': 'reviews_category'
    },
    'genre': {
        'table_name': 'reviews_genre'
    },
    'review': {
        'table_name': 'reviews_review'
    },
}


class Command(BaseCommand):
    """
        Management-команда для импортирования csv-файлов из папки static/data/.

        Из-за того, что файлы не подходят нынешней версии проекта,
        импорт заточен под работу только с ними и для файлов нынешней версии
        потребуется обновление команды.
    """

    help = 'Imports csv data to database'

    def handle(self, *args, **kwargs):
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()

        for file in os.listdir('static/data/'):
            to_db = []
            fieldnames = []

            print(file)

            with open('static/data/' + file) as fin:
                file = file.replace('.csv', '')
                if 'fieldnames' in VALID_DATA[file]:
                    dr = csv.DictReader(
                        fin,
                        fieldnames=VALID_DATA[file]['fieldnames'],
                        restval=''
                    )
                else:
                    dr = csv.DictReader(fin, restval='')

                for row in dr:
                    tuple_row = ()
                    values = ''
                    for j in range(len(dr.fieldnames)):
                        tuple_row += (row[f'{dr.fieldnames[j]}'],)
                        values += '?,'
                    if not (dr.line_num == 1 and 'order' in VALID_DATA[file]):
                        if 'order' in VALID_DATA[file]:
                            tuple_row = tuple(list(
                                tuple_row[i] for i in VALID_DATA[file]['order']
                            ))
                        to_db.append(tuple_row)
                    # else:
                        # wrong_fields = list(tuple_row)
                    tuple_row = ()

            fieldnames = ', '.join(dr.fieldnames)
            if 'fieldnames' not in VALID_DATA[file]:
                fieldnames = ', '.join(dr.fieldnames).replace(
                    'author', 'author_id'
                )

            cur.executemany(
                f"INSERT OR IGNORE INTO {VALID_DATA[file]['table_name']}\
                    ({fieldnames}) VALUES ({values[: -1]});",
                to_db
            )
            to_db.clear()
        con.commit()
        con.close()
