import argparse
import csv
import logging
from threading import Thread

from iot_ready_kit.__init__ import DBSession

from webservice.db_models import Coating, Part

text_short_index = 3
id_index = 2
imos_id_index = 43


def setup_logger():
    logger = logging.getLogger('CoatingImporter')
    logger.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the _logger
    logger.addHandler(ch)

    return logger


class CoatingImporter:
    @staticmethod
    def import_data(csv_file=None, data_string=None):
        logger = setup_logger()
        session = DBSession()

        if csv_file is None and data_string is None:
            logger.error('csv_file and data_string are None, there is no data to import')
            exit()

        logger.info('Starting import script')

        # Delete all coatings
        session.query(Coating).delete()
        session.expire_all()

        coatings = {}
        # Open csv file
        if csv_file:
            with open(csv_file, newline='', encoding='ansi') as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                coatings = CoatingImporter.sum_up_coatings(reader)
        elif data_string:
            rows = data_string.split('\n')
            rows = map(lambda row: row.split(';'), rows)
            coatings = CoatingImporter.sum_up_coatings(rows)

        for imos_id in coatings:
            if imos_id != '0':  # Ignore coatings not associated with any part

                # Create only coating if part exists in db
                if session.query(Part).filter_by(imos_id=imos_id).first():
                    for coating_id in coatings[imos_id]:
                        try:
                            part_number = session.query(Part).filter_by(imos_id=imos_id).first().part_number
                            coating = Coating(part_number=part_number,
                                              name=coating_id,
                                              text_short=coatings[imos_id][coating_id]['text_short'],
                                              count=coatings[imos_id][coating_id]['count'])
                            session.add(coating)
                            session.commit()

                            logging.info('Created coating successfully')
                        except Exception as e:
                            logger.error('Error while creating coating: {}'.format(e))

        session.expire_all()
        session.close()
        logger.info('Finished importing data')

    @staticmethod
    def import_coating_opcua_call(parent, data_string):
        """Make a thread for DataImport so we don't block the client"""
        from opcua import ua
        Thread(target=CoatingImporter.import_data, kwargs=dict(data_string=data_string.Value)).start()
        return [ua.Variant(True, ua.VariantType.Boolean)]

    @staticmethod
    def sum_up_coatings(iterable):
        coatings = {}
        for row in iterable:
            if row[imos_id_index] in coatings and row[id_index] in coatings[row[imos_id_index]]:
                coatings[row[imos_id_index]][row[id_index]]['count'] += 1
            elif row[imos_id_index] in coatings:
                coatings[row[imos_id_index]][row[id_index]] = {'text_short': row[text_short_index], 'count': 1}
            else:
                coatings[row[imos_id_index]] = {}
                coatings[row[imos_id_index]][row[id_index]] = {'text_short': row[text_short_index], 'count': 1}
        return coatings


if __name__ == '__main__':
    commandline_parser = argparse.ArgumentParser(description='Options for DataImport')
    commandline_parser.add_argument('-csv', type=str, metavar='pathtocsv', required=True,
                                    help='the path to the csv file that should be imported')
    args = commandline_parser.parse_args()

    setup_logger()
    CoatingImporter.import_data(csv_file=args.csv)
