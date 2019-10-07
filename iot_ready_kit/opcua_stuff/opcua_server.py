from threading import Thread
import time
import logging
from pathlib import Path

from iot_ready_kit.common.data_import import DataImporter
from iot_ready_kit.common.coating_import import CoatingImporter
from iot_ready_kit.common.db_client import DBClient
from iot_ready_kit.__init__ import config_folder

from opcua import ua, uamethod, Server


class OPCUAServer:
    def __init__(self, ip_address, port, art_net_server=None, carriage=False):
        self._logger = logging.getLogger(__name__)
        self._art_net_server = art_net_server
        self._carriage = carriage
        self._port = port
        self._ip_address = ip_address
        self.thread_run_ok = True
        self.thread = Thread(target=self.server, args=())

    def server(self):
        # Now setup our server
        server = Server()
        server.set_endpoint('opc.tcp://' + self._ip_address + ':' + self._port + '/')
        server.set_server_name('IoT Ready Kit opcua-Server')

        if Path(config_folder + '/privkey.pem').is_file() and Path(config_folder + '/cert.pem').is_file():
            # Load certificates -> fileending has to be .pem
            # https://github.com/FreeOpcUa/python-opcua/issues/456
            server.load_certificate(config_folder + "/cert.pem")
            server.load_private_key(config_folder + "/privkey.pem")

            # Set security policys
            server.set_security_policy([
                ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256_Sign])

        # vars
        carriage_name = None
        carriage_status = None

        # Setup namespaces
        carriage_ns = server.register_namespace('carriage')
        artnet_ns = server.register_namespace('artnet')

        if self._carriage:
            carriage_obj = server.nodes.objects.add_object(carriage_ns, 'iot_ready_kit')
            carriage_name = carriage_obj.add_variable(carriage_ns, 'carriage_name', '')
            carriage_status = carriage_obj.add_variable(carriage_ns, 'carriage_status', '')
            carriage_location = carriage_obj.add_variable(carriage_ns, 'carriage_location', '')
            carriage_obj.add_method(carriage_ns, 'carriage_import_order_data', DataImporter.import_data_opcua_call,
                                    [ua.VariantType.String])
            carriage_obj.add_method(carriage_ns, 'carriage_import_coating_data', CoatingImporter.import_coating_opcua_call,
                                    [ua.VariantType.String])
            carriage_obj.add_method(carriage_ns, 'find_part', self.find_part, [ua.VariantType.String])

        if self._art_net_server:
            artnet_obj = server.nodes.objects.add_object(artnet_ns, 'art_net')

            for node in self._art_net_server.art_net_nodes:
                # Add method illuminate_slot
                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_slot', node.illuminate_slot_opcua_call,
                                      [ua.VariantType.String, ua.VariantType.String], [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_slot_with_history', node.illuminate_slot_with_history_opcua_call,
                                      [ua.VariantType.String, ua.VariantType.String, ua.VariantType.UInt64], [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_slot_dont_coll_history', node.illuminate_slot_dont_coll_history_opcua_call,
                                      [ua.VariantType.String, ua.VariantType.String], [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_multiple_slots', node.illuminate_multiple_slots_opcua_call,
                                      [ua.VariantType.String, ua.VariantType.String], [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_universe', node.illuminate_universe_opcua_call,
                                      [ua.VariantType.UInt64, ua.VariantType.String], [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_universe_rgb', node.illuminate_universe_rgb_opcua_call,
                                      [ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.Int64],
                                      [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_all', node.illuminate_all_opcua_call,
                                      [ua.VariantType.String], [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_from_to', node.illuminate_from_to_opcua_call,
                                      [ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.String],
                                      [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_illuminate_from_to_rgb',
                                      node.illuminate_from_to_rgb_opcua_call,
                                      [ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64,
                                       ua.VariantType.UInt64, ua.VariantType.UInt64, ua.VariantType.UInt64],
                                      [ua.VariantType.Boolean])

                artnet_obj.add_method(artnet_ns, node.name + '_all_off', node.all_off_opcua_call,
                                      '', [ua.VariantType.Boolean])

        # Start server
        try:
            server.start()
            self._logger.info('opcua-Server started')

            while self.thread_run_ok:
                if self._carriage:
                    carriage = DBClient.get_carriage()
                    carriage_location.set_value(carriage.current_location)
                    carriage_name.set_value(carriage.carriage_name)
                    carriage_status.set_value(carriage.carriage_status)
                time.sleep(2)

            server.stop()
            self._logger.info('opcua-Server stopped')
        except OSError as e:
            self.thread_run_ok = False
            self._logger.critical('OS error: {}'.format(e))

    def start_server(self):
        self.thread_run_ok = True
        self.thread.start()

    def stop_server(self):
        self.thread_run_ok = False

    @uamethod
    def find_part(self, parent, part_number):
        slot = DBClient.get_slot_by_part_number(part_number)
        if slot:
            self._logger.info('Found part {} in slot {}'.format(part_number, slot.slot_name))
            self._art_net_server.art_net_nodes[0].illuminate_slot_dont_coll_history(slot.slot_name, 'magenta')
