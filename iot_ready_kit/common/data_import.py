import argparse
import csv
import logging
from datetime import datetime
from threading import Thread

from iot_ready_kit.__init__ import DBSession

from webservice.db_models import Order, Part, ProductionStep, AssemblyGroup, Slot, Coating


def setup_logger():
    logger = logging.getLogger('DataImporter')
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


class DataImporter:
    @staticmethod
    def import_data(csv_file=None, data_string=None):
        logger = setup_logger()

        if csv_file is None and data_string is None:
            logger.error('csv_file and data_string are None, there is no data to import')
            exit()

        session = DBSession()
        logger.info('Starting import script')
        logger.info('Starting cleaning database')

        # Empty slots
        for slot in session.query(Slot).all() or []:
            slot.part_number = None
            session.add(slot)
        session.commit()

        # Delete coating
        session.query(Coating).delete()

        # Delete production steps
        session.query(ProductionStep).delete()

        # Delete parts
        session.query(Part).delete()
        
        # Delete assembly groups
        session.query(AssemblyGroup).delete()

        # Delete orders
        session.query(Order).delete()
        session.commit()
        session.expire_all()

        logger.info('Finishing cleaning of database')
        logger.info('Starting import of data')

        # Open csv file
        if csv_file:
            with open(csv_file, newline='', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    DataImporter._for_row(row, logger, session)
        elif data_string:
            for row in data_string.split('\n'):
                DataImporter._for_row(row.split(';'), logger, session)

        logger.info('Finished importing data')

    @staticmethod
    def import_data_opcua_call(parent, data_string):
        """Make a thread for DataImport so we don't block the client"""
        from opcua import ua
        Thread(target=DataImporter.import_data, kwargs=dict(data_string=data_string.Value)).start()
        return [ua.Variant(True, ua.VariantType.Boolean)]

    @staticmethod
    def _for_row(row, logger, session):
        order_id = None
        # Create order if not existing
        try:
            if session.query(Order).filter_by(customer_order=row[22]).first() is None:
                # If delivery_date casting to datetime fails set it to None
                try:
                    delivery_date = datetime.strptime(row[25], '%d.%m.%Y  %H:%M:%S')
                except ValueError:
                    delivery_date = None

                # If shipping_date casting to datetime fails set it to None
                try:
                    shipping_date = datetime.strptime(row[26], '%d.%m.%Y  %H:%M:%S')
                except ValueError:
                    shipping_date = None

                session.add(Order(customer_order=row[22],
                                  customer=row[23],
                                  delivery_date=delivery_date,
                                  shipping_date=shipping_date))
                session.commit()

            order_id = session.query(Order).filter_by(customer_order=row[22]).first().id
            logger.info('Created order {} successfully'.format(order_id))
        except Exception as e:
            logger.error('Error while creating order: {}'.format(e))

        # Create assembly group if not existing
        if session.query(AssemblyGroup).filter_by(order_id=order_id, part_mapping=row[24]).first() is None:
            # TODO extract group_name from PNX
            group_name = ''

            try:
                session.add(AssemblyGroup(part_mapping=row[24],
                                          group_name=group_name,
                                          assembled=False,
                                          order_id=order_id))
                session.commit()
                logger.info('Created assembly group with part mapping {} successfully'.format(row[24]))
            except Exception as e:
                logger.error('Error while creating assembly group: {}'.format(e))

        # Create part
        try:
            # If untercapacity field cannot be casted set it to zero
            try:
                untercapacity = int(row[6])
            except ValueError:
                untercapacity = 0

            assembly_group_id = session.query(AssemblyGroup).filter_by(order_id=order_id,
                                                                       part_mapping=row[24]).first().group_id
            part = Part(part_number=int(row[0]),
                        order_id=session.query(Order).filter_by(customer_order=row[22]).first().id,
                        material_code=row[1], finished_length=row[15].split(' x ')[0],
                        finished_width=row[15].split(' x ')[1], finished_thickness=row[15].split(' x ')[2],
                        cut_length=row[2].replace(',', '.'), cut_width=row[3].replace(',', '.'),
                        overcapacity=int(row[5]), undercapacity=untercapacity, grain_id=row[7], description=row[8],
                        extra_route=row[10], pattern_info=row[12], label_info=row[13], edge_transition=row[16],
                        batch_number=row[21], part_mapping=int(row[24]), imos_id=int(row[42]),
                        assembly_group_id=assembly_group_id,
                        status='not_onboard')
            session.add(part)
            session.commit()
            logger.info('Created part {} successfully'.format(part.part_number))
        except Exception as e:
            logger.error('Error while creating part: {}'.format(e))

        DataImporter._create_productionsteps(int(row[0]), row[9], row[17], row[18], row[19], row[20], logger, session)
        session.expire_all()
        session.close()

    @staticmethod
    def _create_productionsteps(part_number, productionsteps, edge_front, edge_back, edge_left, edge_right, logger,
                                session):
        for step in productionsteps.split('_'):
            try:
                if step.startswith('EB'):
                    edge_dict = {'front': edge_front, 'back': edge_back, 'left': edge_left, 'right': edge_right}
                    for edge, data in edge_dict.items():
                        session.add(ProductionStep(part_number=part_number,
                                                   name=step,
                                                   status='outstanding',
                                                   edge_value=data,
                                                   edge_position=edge))
                        session.commit()
                else:
                    session.add(ProductionStep(part_number=part_number, name=step, status='outstanding'))
                    session.commit()

                logger.info('Created production step successfully')
            except Exception as e:
                logger.error('Error while creating production step: {}'.format(e))


if __name__ == '__main__':
    commandline_parser = argparse.ArgumentParser(description='Options for DataImport')
    commandline_parser.add_argument('-csv',
                                    type=str,
                                    metavar='pathtocsv',
                                    required=True,
                                    help='the path to the csv file that should be imported')
    args = commandline_parser.parse_args()

    setup_logger()
    DataImporter.import_data(csv_file=args.csv)
