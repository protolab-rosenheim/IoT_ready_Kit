import configparser
import logging
import hashlib

from iot_ready_kit.__init__ import DBSession, irk_conf, carriage_conf, carriage_conf_path, hashes_conf_path

from webservice.db_models import Module, Slot, Carriage


class SlotController:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def prepare_database(self):
        if self._check_if_config_has_changed():
            try:
                session = DBSession()

                session.query(Slot).delete()
                session.query(Module).delete()

                carriage = session.query(Carriage).filter_by(carriage_name=irk_conf['general']['carriage_name']).first()

                # Create modules
                for sel_module in carriage_conf.keys():
                    session.add(Module(module_number=sel_module.split('_')[1],
                                       carriage_id=carriage.id,
                                       max_length=int(carriage_conf[sel_module]['max_length']),
                                       max_width=int(carriage_conf[sel_module]['max_width']),
                                       max_thickness=int(carriage_conf[sel_module]['max_thickness'])))
                    session.commit()

                # Create slots
                for sel_module in carriage_conf.keys():
                    module_number = sel_module.split('_')[1]

                    for i in range(1, int(carriage_conf[sel_module]['num_slots']) + 1):
                        session.add(Slot(slot_name=module_number + '.' + str(i),
                                         part_number=None,
                                         module_number=module_number,
                                         max_length=float(carriage_conf[sel_module]['max_length']),
                                         max_width=float(carriage_conf[sel_module]['max_width']),
                                         max_thickness=float(carriage_conf[sel_module]['max_thickness'])))
                        session.commit()

                return True
            except Exception as e:
                self._logger.error('Error creating modules or slots: {}'.format(e))
                return False

    def _check_if_config_has_changed(self):
        config_hashes_path = hashes_conf_path
        # Calculate md5 of carriage.ini
        md5_carriage_ini = hashlib.md5()
        with open(carriage_conf_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_carriage_ini.update(chunk)

        hash_config = configparser.ConfigParser()
        try:
            hash_config.read(config_hashes_path)
            md5_from_ini = hash_config['carriage_ini']['md5_hash']
        except Exception:
            self.write_carriage_md5(md5_carriage_ini.hexdigest(), config_hashes_path)
            return True

        if md5_from_ini == md5_carriage_ini.hexdigest():
            return False
        else:
            self.write_carriage_md5(md5_carriage_ini.hexdigest(), config_hashes_path)
            return True

    @staticmethod
    def write_carriage_md5(md5_hash, file_path):
        hash_config = configparser.ConfigParser()
        try:
            hash_config.read(file_path)
        except Exception:
            pass
        if 'carriage_ini' not in hash_config.sections():
            hash_config.add_section('carriage_ini')
        hash_config.set('carriage_ini', 'md5_hash', md5_hash)
        with open(file_path, 'w') as cfg_file:
            hash_config.write(cfg_file)
            cfg_file.close()
