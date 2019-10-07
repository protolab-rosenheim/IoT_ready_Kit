import logging

from iot_ready_kit.__init__ import irk_conf, session

from webservice.db_models import Carriage, Part, ProductionStep, Slot


class DBClient:
    @staticmethod
    def _get_logger():
        return logging.getLogger(__name__)

    @staticmethod
    def check_db_connection():
        try:
            session.query(Carriage).first()
            session.expire_all()
            return True
        except Exception:
            return False

    @staticmethod
    def cre_carriage(carriage):
        try:
            session.add(carriage)
            session.commit()
            session.expire_all()
            return True
        except Exception as e:
            DBClient._get_logger().error('db connection(upd_carriage) error: {}'.format(e))
            return False

    @staticmethod
    def get_carriage():
        try:
            return session.query(Carriage).filter_by(carriage_name=irk_conf['general']['carriage_name']).first()
        except Exception as e:
            DBClient._get_logger().error('db connection(get_carriage) error: {}'.format(e))
            return None
        finally:
            session.expire_all()

    @staticmethod
    def upd_carriage(carriage):
        try:
            session.add(carriage)
            session.commit()
            session.expire_all()
            return True
        except Exception as e:
            DBClient._get_logger().error('db connection(upd_carriage) error: {}'.format(e))
            return False

    @staticmethod
    def get_part(part_num):
        try:
            return session.query(Part).filter_by(part_number=int(part_num)).first()
        except ValueError:
            return None
        except Exception as e:
            DBClient._get_logger().error('db connection(get_part) error: {}'.format(e))
            return None
        finally:
            session.expire_all()

    @staticmethod
    def upd_part(part):
        try:
            session.add(part)
            session.commit()
            session.expire_all()
            return True
        except Exception as e:
            DBClient._get_logger().error('db connection(upd_part) error: {}'.format(e))
            return False

    @staticmethod
    def get_prod_step_outstanding():
        try:
            return session.query(ProductionStep).filter_by(status='outstanding').all()
        except Exception as e:
            DBClient._get_logger().error('db connection(get_prod_step_outstanding) error: {}'.format(e))
            return []
        finally:
            session.expire_all()

    @staticmethod
    def get_prod_step_by_part_num(part_num):
        try:
            return session.query(ProductionStep).filter_by(part_number=part_num).all()
        except Exception as e:
            DBClient._get_logger().error('db connection(get_prod_step_by_part_num) error: {}'.format(e))
            return []
        finally:
            session.expire_all()

    @staticmethod
    def upd_prod_step(prod_step):
        try:
            session.add(prod_step)
            session.commit()
            session.expire_all()
            return True
        except Exception as e:
            DBClient._get_logger().error('db connection(upd_prod_step) error: {}'.format(e))
            return False

    @staticmethod
    def get_suitable_slots(lenght, width, thickness):
        try:
            return session.query(Slot).filter('max_length' >= str(lenght),
                                              'max_width' >= str(width),
                                              'max_thickness' >= str(thickness),
                                              'part_number' == None).all()
        except Exception as e:
            DBClient._get_logger().error('db connection(get_suitable_slots) error: {}'.format(e))
            return []
        finally:
            session.expire_all()

    @staticmethod
    def get_slot_by_part_number(part_num):
        try:
            return session.query(Slot).filter_by(part_number=part_num).first()
        except Exception as e:
            DBClient._get_logger().error('db connection(find_slot_by_part_number) error: {}'.format(e))
            return None
        finally:
            session.expire_all()

    @staticmethod
    def upd_slot(slot):
        try:
            session.add(slot)
            session.commit()
            session.expire_all()
            return True
        except Exception as e:
            DBClient._get_logger().error('db connection(upd_slot) error: {}'.format(e))
            return False