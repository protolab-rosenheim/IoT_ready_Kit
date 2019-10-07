import logging
import logging.config
import json
import os
import time
import socket

from iot_ready_kit.opcua_stuff.opcua_server import OPCUAServer
from artnet.artnet_configurator import ArtNetConfigurator
from iot_ready_kit.controllers.carriage_control import CarriageControl
from iot_ready_kit.__init__ import irk_conf_path, led_mapping_conf_path, modules_section, irk_conf, config_folder, db_host, db_port
from iot_ready_kit.common.db_client import DBClient
from iot_ready_kit.opcua_stuff.opcua_client import OPCUAClient


def setup_logging(path_to_config, default_level=logging.INFO):
    if os.path.exists(path_to_config):
        with open(path_to_config, 'rt') as config_file:
            config = json.load(config_file)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    check_sleep_time = 5
    check_threads_sleep_time = 5
    start_illuminate_time = 5
    artnet_server = None
    thread_list = []

    # Setup _logger
    setup_logging(config_folder + '/logging.json')
    logger = logging.getLogger(__name__)

    # Wait till database is available
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((db_host, int(db_port)))
        if result == 0:
            logger.warning("Database is available")
            time.sleep(check_sleep_time)
            break
        else:
            logger.warning("Waiting for database availability")
        time.sleep(check_sleep_time)

    logger.info('IOTStarter starting services')

    # Starting ArtNetServer
    if modules_section['artnet_server']:
        artnet_configurator = ArtNetConfigurator()
        artnet_server = artnet_configurator.get_artnet_server(irk_conf_path, led_mapping_conf_path)
        artnet_server.start_server()
        thread_list.append(artnet_server.thread)

    # Starting OPCUAServer
    if modules_section['opcua_server']:
        opcua_server = OPCUAServer(irk_conf['opcua_server']['ip_address'],
                                   irk_conf['opcua_server']['port'],
                                   artnet_server,
                                   modules_section['carriage'])
        opcua_server.start_server()
        thread_list.append(opcua_server.thread)

    # Starting CarriageController
    if modules_section['carriage']:
        carriage_control = CarriageControl()
        carriage_control.start_controller()
        thread_list.append(carriage_control.thread)

    logger.info('IOTStarter started services')

    # Wait for opcua server startup
    opcua_client = OPCUAClient('opc.tcp://' + irk_conf['opcua_server']['ip_address'] + ':' +
                               irk_conf['opcua_server']['port'] + '/')
    while not opcua_client.check_opcua_connection():
        logger.warning("Waiting for opcua server availability")
        time.sleep(check_sleep_time)

    # Illuminate all slots after startup
    opcua_client.illuminate_all('green')
    time.sleep(start_illuminate_time)
    opcua_client.all_off()

    # Run till every thread has finished
    while thread_list:
        time.sleep(check_threads_sleep_time)
        for thread in thread_list:
            if not thread.isAlive():
                thread_list.remove(thread)
