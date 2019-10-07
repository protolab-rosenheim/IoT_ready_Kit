from copy import deepcopy
from iot_ready_kit.ArtNet.ArtNetNode import ArtNetNode, LEDStrip
from iot_ready_kit.ArtNet.Packets import ArtNetDMXPacket, PacketType
from Webservice.DBModels import Carriage, Module, Slot, Part


class ArtNetDemoData:
    @staticmethod
    def artnet_dmx_data(exam_num):
        if exam_num == 1:
            return deepcopy(ArtNetDMXPacket(PacketType.ART_DMX, 1, 0, 1, LEDStrip(20).to_byte_array()))
        elif exam_num == 2:
            return deepcopy(ArtNetDMXPacket(PacketType.ART_DMX, 1, 0, 1, LEDStrip(20).to_byte_array()))
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def artnet_get_universe(exam_num):
        if exam_num == 1:
            return deepcopy({1: LEDStrip(20), 3: LEDStrip(40)})

    @staticmethod
    def artnet_get_slot(exam_num):
        if exam_num == 1:
            return deepcopy({'slot_1.1': {'universe': 1, 'led': '0-5'}, 'slot_1.2': {'universe': 1, 'led': '6-15'},
                             'slot_1.3': {'universe': 1, 'led': '16-19'}, 'slot_2.1': {'universe': 3, 'led': '0-5'},
                             'slot_2.2': {'universe': 3, 'led': '6-10'}, 'slot_2.3': {'universe': 3, 'led': '11-20'},
                             'slot_2.4': {'universe': 3, 'led': '21-30'}, 'slot_2.5': {'universe': 3, 'led': '31-39'}})
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def artnet_get_node(exam_num):
        if exam_num == 1:
            art_net_node = ArtNetNode('TestNode', '10.10.10.30', 6454, 5)
            art_net_node.universe = ArtNetDemoData.artnet_get_universe(1)
            art_net_node.slots = ArtNetDemoData.artnet_get_slot(1)
            return deepcopy(art_net_node)
        elif exam_num == 2:
            art_net_node = ArtNetNode('TestNode', '10.10.10.30', 6454, 5)
            art_net_node.universe = ArtNetDemoData.artnet_get_universe(1)
            art_net_node.slots = ArtNetDemoData.artnet_get_slot(1)
            art_net_node.color_history = ['yellow', 'orange', 'red']
            return deepcopy(art_net_node)
        else:
            raise ValueError('Example not found -> ', exam_num)


class IniDemoData:
    @staticmethod
    def ini_get_carriage_ini(exam_num):
        if exam_num == 1:
            return deepcopy(
                {"module_1": {"max_length": "2300", "max_width": "790", "max_thickness": "10", "num_slots": "5"},
                 "module_2": {"max_length": "780", "max_width": "370", "max_thickness": "20", "num_slots": "5"}})
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def ini_get_iot_ready_kit_ini(exam_num):
        if exam_num == 1:
            return deepcopy({"general": {"carriage_name": "carriage001"}})
        else:
            raise ValueError('Example not found -> ', exam_num)


class DBModelsDemoData:
    @staticmethod
    def dbmodels_get_carriage(exam_num):
        if exam_num == 1:
            return deepcopy(Carriage(id=1, carriage_name='carriage001', carriage_status='not in use',
                                     current_location='parked', next_location='na',
                                     destacking_mode='SimpleDistribute'))
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def dbmodels_get_module(exam_num):
        if exam_num == 1:
            return deepcopy(Module(module_number=1, carriage_id=1, max_length=2300, max_width=790, max_thickness=10))
        elif exam_num == 2:
            return deepcopy(Module(module_number=2, carriage_id=1, max_length=780, max_width=370, max_thickness=20))
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def dbmodels_get_slot(exam_num):
        if exam_num == 1:
            return deepcopy(Slot(slot_name='1.1', part_number=None, module_number=1, max_length=300.0, max_width=120.0,
                                 max_thickness=10.0))
        elif exam_num == 2:
            return deepcopy(Slot(slot_name='1.2', part_number=None, module_number=1, max_length=300.0, max_width=120.0,
                                 max_thickness=10.0))
        elif exam_num == 3:
            return deepcopy(Slot(slot_name='2.1', part_number=None, module_number=2, max_length=600.0, max_width=500.0,
                                 max_thickness=15.0))
        elif exam_num == 4:
            return deepcopy(Slot(slot_name='2.2', part_number=None, module_number=2, max_length=600.0, max_width=500.0,
                                 max_thickness=15.0))
        elif exam_num == 5:
            return deepcopy(Slot(slot_name='3.1', part_number=None, module_number=3, max_length=20.0, max_width=20.0,
                                 max_thickness=15.0))
        elif exam_num == 6:
            return deepcopy(Slot(id=33, slot_name='2.18', part_number=1833, module_number=2, max_length=1600,
                                 max_width=630, max_thickness=40))
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def dbmodels_get_slot_list(exam_num):
        if exam_num == 1:
            return deepcopy([DBModelsDemoData.dbmodels_get_slot(1), DBModelsDemoData.dbmodels_get_slot(2),
                             DBModelsDemoData.dbmodels_get_slot(3)])
        elif exam_num == 2:
            return deepcopy([DBModelsDemoData.dbmodels_get_slot(1), DBModelsDemoData.dbmodels_get_slot(2),
                             DBModelsDemoData.dbmodels_get_slot(3), DBModelsDemoData.dbmodels_get_slot(4),
                             DBModelsDemoData.dbmodels_get_slot(5)])
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def dbmodels_get_part(exam_num):
        if exam_num == 1:
            return deepcopy(
                Part(part_number=11, order_id=1, material_code='DTP_NGR_PRL_18_White', finished_length=230.5,
                     finished_width=100.3, finished_thickness=5.0, cut_length=229.5, cut_width=99.3,
                     overcapacity=0, undercapacity=0, grain_id=0, description='Einlegeboden',
                     edge_transition='011:011:000:000', status='not_onboard', batch_number='20170922-0004',
                     extra_route='-', label_info='', part_mapping=1, pattern_info=''))
        elif exam_num == 2:
            return deepcopy(
                Part(part_number=12, order_id=1, material_code='DTP_NGR_PRL_18_White', finished_length=900.0,
                     finished_width=100.3, finished_thickness=5.0, cut_length=899.5, cut_width=99.3,
                     overcapacity=0, undercapacity=0, grain_id=0, description='Einlegeboden',
                     edge_transition='011:011:000:000', status='not_onboard', batch_number='20170922-0004',
                     extra_route='-', label_info='', part_mapping=1, pattern_info=''))
        elif exam_num == 3:
            return deepcopy(
                Part(part_number=13, order_id=1, material_code='DTP_NGR_PRL_18_White', finished_length=285.5,
                     finished_width=110.3, finished_thickness=5.0, cut_length=227.5, cut_width=99.3,
                     overcapacity=0, undercapacity=0, grain_id=0, description='Einlegeboden',
                     edge_transition='011:011:000:000', status='not_onboard', batch_number='20170922-0004',
                     extra_route='-', label_info='', part_mapping=1, pattern_info=''))
        else:
            raise ValueError('Example not found -> ', exam_num)


class RestClientDemoData:
    @staticmethod
    def restclient_get_data_part(exam_num):
        if exam_num == 1:
            return deepcopy({
                "part_number": 11, "order_id": 1, "material_code": "DTP_NGR_PRL_18_White", "finished_length": 230.5,
                "finished_width": 100.3, "finished_thickness": 5.0, "cut_length": 229.5, "cut_width": 99.3,
                "overcapacity": 0, "undercapacity": 0, "grain_id": 0, "description": "Einlegeboden",
                "edge_transition": "011:011:000:000",  "status": "not_onboard", "batch_number": "20170922-0004",
                "extra_route": "-", "label_info": "", "part_mapping": 1, "pattern_info": ""})
        elif exam_num == 2:
            return deepcopy({
                "part_number": 12, "order_id": 1, "material_code": "DTP_NGR_PRL_18_White", "finished_length": 900.0,
                "finished_width": 100.3, "finished_thickness": 5.0, "cut_length": 899.5, "cut_width": 99.3,
                "overcapacity": 0, "undercapacity": 0, "grain_id": 0, "description": "Einlegeboden",
                "edge_transition": "011:011:000:000", "status": "not_onboard", "batch_number": "20170922-0004",
                "extra_route": "-", "label_info": "", "part_mapping": 1, "pattern_info": ""})
        elif exam_num == 3:
            return deepcopy({
                "part_number": 13, "order_id": 1, "material_code": "DTP_NGR_PRL_18_White", "finished_length": 285.5,
                "finished_width": 110.3, "finished_thickness": 5.0, "cut_length": 227.5, "cut_width": 99.3,
                "overcapacity": 0, "undercapacity": 0, "grain_id": 0, "description": "Einlegeboden",
                "edge_transition": "011:011:000:000", "status": "not_onboard", "batch_number": "20170922-0004",
                "extra_route": "-", "label_info": "", "part_mapping": 1, "pattern_info": ""})
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def restclient_get_data_slot(exam_num):
        if exam_num == 1:
            return deepcopy({"id": 33, "max_length": 1600, "max_thickness": 40, "max_width": 630, "module_number": 2,
                             "part_number": 1833, "slot_name": "2.18"})
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def restclient_get_data_part_list(exam_num):
        if exam_num == 1:
            return [RestClientDemoData.restclient_get_data_part(1), RestClientDemoData.restclient_get_data_part(2),
                    RestClientDemoData.restclient_get_data_part(3)]
        else:
            raise ValueError('Example not found -> ', exam_num)

    @staticmethod
    def restclient_get_data_slot_list(exam_num):
        if exam_num == 1:
            return [RestClientDemoData.restclient_get_data_slot(1)]
        else:
            raise ValueError('Example not found -> ', exam_num)
