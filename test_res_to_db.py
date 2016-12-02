import pickle
import MySQLdb
from secrets import *
import argparse
import json
import itertools
from dist2coast import dist2coast


def db_connect():
    try:
        return MySQLdb.connect(cnx['HOST'], cnx['USER'], cnx['PASSWORD'], cnx['db'], charset='utf8', use_unicode=True)
    except Exception as e:
        print("Cannot connect")
        print(e)
        return None


def insert_pickle_data(db):

    with open('test_results.pkl', 'rb') as pkl:
        data = pickle.load(pkl)

    test_ships_mmsi = data['test_ships_mmsi']
    predicted_labels = data['predicted_labels']

    assert len(test_ships_mmsi) == len(predicted_labels)

    values = ''
    for idx in range(0, len(test_ships_mmsi)-1):
        values += "({},'{}'),".format(test_ships_mmsi[idx], predicted_labels[idx])
    values = values[:-1]

    cursor = db.cursor()
    st = "INSERT INTO ships_classified (mmsi, `class`) VALUES " + values + ";"

    try:
        cursor.execute(st)
        db.commit()
    except Exception:
        print("FUCKKKK")
    finally:
        cursor.close()


if __name__ == '__main__':
    db = db_connect()
    insert_pickle_data(db)


