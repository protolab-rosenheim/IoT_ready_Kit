import logging

from opcua import Client


class OPCUAClient:
    def __init__(self, opcua_url):
        self.client = Client(opcua_url)
        self.subscribe_handle = None
        self.subscriber = None
        self.logger = logging.getLogger(__name__)

    def check_opcua_connection(self):
        try:
            self.client.connect()
            root_node = self.client.get_root_node()
            server = root_node.get_child(['0:Objects', '0:Server'])
            if len(server.get_children()) > 0:
                self.client.disconnect()
                return True
            else:
                return False
        except Exception as e:
            return False

    def subscribe(self, class_to_call, machine):
        try:
            self.client.connect()
            node_path = ''
            if machine == 'SAW':
                node_path = ['0:Objects', '2:Saw', '2:PartName']
            elif machine == 'DRILL':
                node_path = ['0:Objects', '2:BHX', '2:bhx_status']
            else:
                node_path = 'FAULTY'

            node = self.client.get_root_node().get_child(node_path)
            self.subscriber = self.client.create_subscription(500, class_to_call)
            self.subscribe_handle = self.subscriber.subscribe_data_change(node)
            return True
        except Exception as e:
            self.logger.critical('Error while subscribing to {}: {}'.format(e, node_path))
            return False

    def unsubscribe(self):
        if self.subscriber:
            try:
                self.subscriber.unsubscribe(self.subscribe_handle)
                self.subscriber.delete()
                self.subscribe_handle = None
                self.client.disconnect()
            except Exception as e:
                self.logger.critical('Error while UNsubscribing to saw or drill: {}'.format(e))

    def illuminate_slot(self, slot, color):
        try:
            self.client.connect()
            root_node = self.client.get_root_node()
            illuminate_slot = root_node.get_child(['0:Objects', '3:art_net', '3:node_1_illuminate_slot'])
            if illuminate_slot:
                res_call = root_node.call_method(illuminate_slot, slot, color)
                return res_call
            else:
                return False
        except Exception as e:
            self.logger.critical('Error while illuminate_slot: {}'.format(e))
        finally:
            self.client.disconnect()

    def illuminate_slot_with_history(self, slot, color, history_to_illu):
        try:
            self.client.connect()
            root_node = self.client.get_root_node()
            illuminate_slot_with_history = root_node.get_child(['0:Objects', '3:art_net', '3:node_1_illuminate_slot_with_history'])
            if illuminate_slot_with_history:
                res_call = root_node.call_method(illuminate_slot_with_history, slot, color, history_to_illu)
                return res_call
            else:
                return False
        except Exception as e:
            self.logger.critical('Error while illuminate_slot_with_history: {}'.format(e))
        finally:
            self.client.disconnect()

    def illuminate_all(self, color):
        try:
            self.client.connect()
            root_node = self.client.get_root_node()
            illuminate_all = root_node.get_child(['0:Objects', '3:art_net', '3:node_1_illuminate_all'])
            if illuminate_all:
                res_call = root_node.call_method(illuminate_all, color)
                return res_call
            else:
                return False
        except Exception as e:
            self.logger.critical('Error while illuminate_all: {}'.format(e))
        finally:
            self.client.disconnect()

    def all_off(self):
        try:
            self.client.connect()
            root_node = self.client.get_root_node()
            all_off = root_node.get_child(['0:Objects', '3:art_net', '3:node_1_all_off'])
            if all_off:
                res_call = root_node.call_method(all_off)
                return res_call
            else:
                return False
        except Exception as e:
            self.logger.critical('Error while all_off: {}'.format(e))
        finally:
            self.client.disconnect()
