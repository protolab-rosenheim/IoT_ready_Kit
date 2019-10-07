from nose.tools import assert_equal, assert_list_equal, assert_dict_equal
from iot_ready_kit.ArtNet.ArtNetNode import LEDStrip
from iot_ready_kit.ArtNet.Packets import ArtNetDMXPacket, PacketType
from test_iot_ready_kit.resources.demo_data import ArtNetDemoData

slot_example_1 = {'slot_1.1': {'universe': 1, 'led': '0-5'}, 'slot_1.2': {'universe': 1, 'led': '6-15'},
                  'slot_1.3': {'universe': 1, 'led': '16-19'}, 'slot_2.1': {'universe': 3, 'led': '0-5'},
                  'slot_2.2': {'universe': 3, 'led': '6-10'}, 'slot_2.3': {'universe': 3, 'led': '11-20'},
                  'slot_2.4': {'universe': 3, 'led': '21-30'}, 'slot_2.5': {'universe': 3, 'led': '31-39'}}


def test_art_net_node_illuminate_slot_true():
    """ART NET NODE: Check if illuminate_slot returned True"""
    art_net_node = ArtNetDemoData.artnet_get_node(1)

    ret = art_net_node.illuminate_slot('1.1', 'green')

    assert_equal(ret, True)


def test_art_net_node_illuminate_slot_false():
    """ART NET NODE: Check if illuminate_slot returned False"""
    art_net_node = ArtNetDemoData.artnet_get_node(1)

    ret = art_net_node.illuminate_slot('1.5', 'green')

    assert_equal(ret, False)


def test_art_net_node_illuminate_slot_history_ok():
    """ART NET NODE: Check if illuminate_slot returned False"""
    art_net_node = ArtNetDemoData.artnet_get_node(1)

    art_net_node.illuminate_slot('1.1', 'green')
    art_net_node.illuminate_slot('1.1', 'green')
    art_net_node.illuminate_slot('1.2', 'green')
    slot_history = art_net_node.slot_history

    assert_list_equal(slot_history, ['slot_1.2', 'slot_1.1'])


def test_art_net_node_illuminate_slot_check_led_strip():
    """ART NET NODE: Check if illuminate_slot illuminates the correct leds with color x"""
    art_net_node = ArtNetDemoData.artnet_get_node(1)

    art_net_node.illuminate_slot('1.1', 'green')

    led_strip_1 = LEDStrip(20)
    start_led, end_led = art_net_node._extract_start_end_led('slot_1.1')
    led_strip_1 = art_net_node._illuminate_from_to(start_led, end_led, led_strip_1, 'green')
    my_packet = ArtNetDMXPacket(PacketType.ART_DMX, 2, 0, 1,
                                                   led_strip_1.to_byte_array()).packet_to_byte_array()

    assert_equal(art_net_node.send_queue[0], my_packet)


def test_art_net_node_illuminate_slot_with_history():
    """ART NET NODE: Check if illuminate_slot_with_history returns True"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    art_net_node.illuminate_slot('1.1', 'green')
    ret = art_net_node.illuminate_slot_with_history('1.3', 'red', 3)

    assert_equal(ret, True)


def test_art_net_node_history_builder_dict_1():
    """ART NET NODE: Check if _history_builder returns correct dict 1"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    art_net_node.illuminate_slot('1.1', 'green')
    art_net_node.illuminate_slot('2.1', 'green')
    builder_history = art_net_node._history_builder(2.1, 'green', 2)

    assert_dict_equal(builder_history, {'slot_1.1': 'yellow', 'slot_2.1': 'green'})


def test_art_net_node_history_builder_dict_2():
    """ART NET NODE: Check if _history_builder returns correct dict 2"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    art_net_node.illuminate_slot('1.1', 'green')
    art_net_node.illuminate_slot('2.1', 'green')
    builder_history = art_net_node._history_builder(2.1, 'green', -2)

    assert_dict_equal(builder_history, {'slot_2.1': 'green'})


def test_art_net_node_history_builder_dict_3():
    """ART NET NODE: Check if _history_builder returns correct dict 3"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    builder_history = art_net_node._history_builder(2.1, 'green', 2)

    assert_dict_equal(builder_history, {'slot_2.1': 'green'})


def test_art_net_node_history_builder_dict_4():
    """ART NET NODE: Check if _history_builder returns correct dict 4"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    art_net_node.illuminate_slot('1.1', 'green')
    builder_history = art_net_node._history_builder(1.2, 'green', 4)

    assert_dict_equal(builder_history, {'slot_1.1': 'yellow', 'slot_1.2': 'green'})


def test_art_net_node_history_builder_dict_5():
    """ART NET NODE: Check if _history_builder returns correct dict 5"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    art_net_node.illuminate_slot('1.1', 'green')
    art_net_node.illuminate_slot('1.2', 'green')
    art_net_node.illuminate_slot('2.1', 'green')
    builder_history = art_net_node._history_builder('1.3', 'green', 4)

    assert_dict_equal(builder_history,
                      {'slot_1.1': 'red', 'slot_1.2': 'orange', 'slot_2.1': 'yellow', 'slot_1.3': 'green'})


def test_art_net_node_history_led_strip_builder():
    """ART NET NODE: Check if _history_led_strip_builder returns correct dict"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    builder_history = art_net_node._history_led_strip_builder({'slot_1.1': 'yellow', 'slot_2.1': 'green'})

    led_strip_1 = LEDStrip(20)
    led_strip_2 = LEDStrip(40)
    led_strip_1 = art_net_node._illuminate_from_to(0, 5, led_strip_1, 'yellow')
    led_strip_2 = art_net_node._illuminate_from_to(0, 5, led_strip_2, 'green')

    assert_dict_equal(builder_history, {1: led_strip_1, 3: led_strip_2})


def test_art_net_node_history_led_strip_builder_2():
    """ART NET NODE: Check if _history_led_strip_builder returns correct dict 2"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    builder_history = art_net_node._history_led_strip_builder(
        {'slot_1.2': 'yellow', 'slot_1.1': 'green', 'slot_1.3': 'orange'})

    led_strip_1 = LEDStrip(20)
    led_strip_2 = LEDStrip(40)
    led_strip_1 = art_net_node._illuminate_from_to(0, 5, led_strip_1, 'green')
    led_strip_1 = art_net_node._illuminate_from_to(6, 15, led_strip_1, 'yellow')
    led_strip_1 = art_net_node._illuminate_from_to(16, 19, led_strip_1, 'orange')

    assert_dict_equal(builder_history, {1: led_strip_1, 3: led_strip_2})


def test_art_net_node_max_history_size():
    """ART NET NODE: Check if max_history_size works"""
    art_net_node = ArtNetDemoData.artnet_get_node(2)

    art_net_node.illuminate_slot('1.1', 'green')
    art_net_node.illuminate_slot('1.2', 'green')
    art_net_node.illuminate_slot('1.3', 'green')
    art_net_node.illuminate_slot('2.1', 'green')
    art_net_node.illuminate_slot('2.2', 'green')
    art_net_node.illuminate_slot('2.3', 'green')

    assert_equal(art_net_node._max_history_size, 5)
