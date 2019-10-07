from threading import Thread
import logging
import time
import json

from iot_ready_kit.opcua_stuff.opcua_client import OPCUAClient
from iot_ready_kit.controllers.slot_controller import SlotController
from iot_ready_kit.controllers.simple_distribute import SimpleDistribute
from iot_ready_kit.controllers.fit_best_distribute import FitBestDistribute
from iot_ready_kit.__init__ import irk_conf
from iot_ready_kit.common.db_client import DBClient

from webservice.db_models import Carriage


class CarriageControl:
    """
    | CarriageControl is used for navigating the carriage trough the production.
    | Possible status for carriage: in use, waiting for job, faulty, booked
    | At first the carriage is in "waiting for job". If someone would like to use it, he has to
    set the status to "booked" and transfer the required data, after that he has to set the status to "in use"
    and the carriage will find its way.... magic happens!
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.thread_run_ok = True
        self.sleeptime = 1
        self.sleeptime_after_run = 20
        self.led_time_connection_ok = 4
        self.current_prodstep = None
        self._prepare_database()
        self.destacking_mode = self._set_destacking_mode()
        self.opcua_client_local = OPCUAClient('opc.tcp://' + irk_conf['opcua_server']['ip_address'] + ':' +
                                              irk_conf['opcua_server']['port'] + '/')
        self.thread = Thread(target=self.start_trip, args=())

    def start_trip(self):
        self.logger.info('CarriageControl started')
        while self.thread_run_ok:
            while DBClient.get_carriage().carriage_status in ['waiting for job', 'booked']:
                time.sleep(self.sleeptime)

            if DBClient.get_carriage().carriage_status == 'in use':
                self.logger.debug('Started in use')

                while self._get_outstanding_prodsteps():
                    while DBClient.get_carriage().current_location not in ['CU1', 'DR1']:
                        time.sleep(self.sleeptime)

                    self.current_prodstep = DBClient.get_carriage().current_location
                    self._processing()

                self.logger.info('Finished')
                carriage = DBClient.get_carriage()
                carriage.current_location = 'parked'
                carriage.next_location = 'na'
                carriage.carriage_status = 'waiting for job'
                DBClient.upd_carriage(carriage)
        # After every run sleep 5 secs. Implement a "standby" state
        time.sleep(5)

    def _processing(self):
        """Processing for different machines"""
        if self.current_prodstep == 'CU1':
            self._saw_processing()
        if self.current_prodstep == 'DR1':
            self._drill_processing()

        self.current_prodstep = None
        # Sleep xx seconds after that turn all lights to green because we are done at the saw
        time.sleep(self.sleeptime_after_run)
        self.opcua_client_local.illuminate_all('green')
        time.sleep(self.led_time_connection_ok)
        self.opcua_client_local.all_off()

    def _saw_processing(self):
        """Steps that needs to be done if we are at the saw"""
        carriage = DBClient.get_carriage()
        carriage.next_location = 'after_' + self.current_prodstep
        DBClient.upd_carriage(carriage)
        self.logger.debug('At saw, subscribing')
        opcua_client_saw = OPCUAClient(irk_conf['other_devices']['saw_1'])
        self.opcua_client_local.all_off()

        # Try subscribing to saw until it succeeds
        saw_subscribe_ret = opcua_client_saw.subscribe(self, 'SAW')
        while not saw_subscribe_ret and DBClient.get_carriage().current_location == 'CU1':
            saw_subscribe_ret = opcua_client_saw.subscribe(self, 'SAW')
        self.opcua_client_local.illuminate_all('white')
        time.sleep(self.led_time_connection_ok)
        self.opcua_client_local.all_off()

        while self.current_prodstep in self._get_outstanding_prodsteps()\
                and DBClient.get_carriage().current_location == 'CU1':
            # If parts need to pass current prodstep sleep
            time.sleep(self.sleeptime)
        self.logger.debug('Finished at saw, deleting subscription')
        opcua_client_saw.unsubscribe()

        carriage = DBClient.get_carriage()
        carriage.next_location = 'na'
        carriage.current_location = 'after_' + self.current_prodstep
        DBClient.upd_carriage(carriage)

    def _drill_processing(self):
        """Fill with stuff at drilling -> We don't know what we should do here"""
        carriage = DBClient.get_carriage()
        carriage.next_location = 'after_' + self.current_prodstep
        DBClient.upd_carriage(carriage)
        self.logger.debug('At drilling, subscribing')
        opcua_client_drill = OPCUAClient(irk_conf['other_devices']['drill_1'])

        # Try subscribing to drill until it succeeds
        drill_subscribe_ret = opcua_client_drill.subscribe(self, 'DRILL')
        while not drill_subscribe_ret and DBClient.get_carriage().current_location == 'DR1':
            drill_subscribe_ret = opcua_client_drill.subscribe(self, 'DRILL')
        self.opcua_client_local.illuminate_all('white')
        time.sleep(self.led_time_connection_ok)
        self.opcua_client_local.all_off()

        while self.current_prodstep in self._get_outstanding_prodsteps()\
                and DBClient.get_carriage().current_location == 'DR1':
            # If parts need to pass current prodstep sleep
            time.sleep(self.sleeptime)
        self.logger.debug('Finished at drill, deleting subscription')
        opcua_client_drill.unsubscribe()

        carriage = DBClient.get_carriage()
        carriage.next_location = 'na'
        carriage.current_location = 'after_' + self.current_prodstep
        DBClient.upd_carriage(carriage)

    def datachange_notification(self, node, val, data):
        """Gets called if this class has subscribed to a opcua server var"""
        if self.current_prodstep == 'CU1':
            part = DBClient.get_part(val)
            if part and part.status == 'not_onboard':
                prodsteps = DBClient.get_prod_step_by_part_num(part.part_number)
                for step in prodsteps:
                    if step.name == self.current_prodstep:
                        step.status = 'finished'
                        if DBClient.upd_prod_step(step):
                            self.logger.debug('Update of step {} was successfully'.format(str(step.id)))
                        else:
                            self.logger.debug('Update of step {} was failed'.format(str(step.id)))

                self.opcua_client_local.all_off()
                slot = self.destacking_mode.distribute_and_book(val)
                if slot:
                    self.opcua_client_local.illuminate_slot_with_history(slot, 'green', 2)
                else:
                    self.opcua_client_local.illuminate_all('red')
                    self.logger.error('Could not find suitable slot for part: {}'.format(part.part_number))
        if self.current_prodstep == 'DR1' and val:
            bhx_status = json.loads(val)
            part = DBClient.get_part(bhx_status['program_name'])
            if part and part.status == 'onboard' and bhx_status['action'] == 'END':
                prodsteps = DBClient.get_prod_step_by_part_num(part.part_number)
                for step in prodsteps:
                    if step.name == self.current_prodstep:
                        step.status = 'finished'
                        if DBClient.upd_prod_step(step):
                            self.logger.debug('Update of step {} was successfully'.format(str(step.id)))
                        else:
                            self.logger.debug('Update of step {} was failed'.format(str(step.id)))

    def _get_outstanding_prodsteps(self):
        """
        | Collects outstanding production steps
        | :return: set with outstanding production steps
        """
        # TODO: Make set in DB query?
        prodsteps = DBClient.get_prod_step_outstanding()
        prodsteps_set = set()
        for step in prodsteps:
            prodsteps_set.add(step.name)
        return sorted(prodsteps_set)

    def _prepare_database(self):
        """
        Prepares the database. At first creates or updates carriage, after that it calls the SlotManagement for
        creating and updating the slots.
        """

        # If carriage not exists create it. If it's existing update it
        if DBClient.get_carriage() is None:
            if DBClient.cre_carriage(self._setup_carriage()):
                self.logger.info('Successfully created carriage in database')
            else:
                self.logger.error('Could not create carriage in database, exiting')
                exit()
        else:
            carriage = DBClient.get_carriage()
            carriage = self._setup_carriage(carriage=carriage)
            if DBClient.upd_carriage(carriage):
                self.logger.info('Successfully updated carriage in database')
            else:
                self.logger.error('Could not update carriage in database, exiting')
                exit()

        slot_controller = SlotController()
        slot_controller.prepare_database()

    def _set_destacking_mode(self):
        mode = DBClient.get_carriage().destacking_mode
        if mode == 'SimpleDistribute':
            return SimpleDistribute()
        elif mode == 'FitBestDistribute':
            return FitBestDistribute()
        else:
            # Fallback is SimpleDistribute
            return SimpleDistribute()

    def _setup_carriage(self, carriage=None):
        """
        Initially creates a carriage or resets the attributes of a carriage provided as parameter
        :param carriage:
        :return: The newly created or reset carriage
        """
        if carriage is None:
            carriage = Carriage()

        carriage.carriage_name = irk_conf['general']['carriage_name']
        carriage.carriage_status = 'waiting for job'
        carriage.current_location = 'parking lot'
        carriage.next_location = 'na'
        carriage.destacking_mode = irk_conf['general']['destacking_mode']
        return carriage

    def start_controller(self):
        self.thread_run_ok = True
        self.thread.start()

    def stop_controller(self):
        self.thread_run_ok = False
