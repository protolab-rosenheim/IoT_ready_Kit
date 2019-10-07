from nose.tools import assert_equal, assert_not_equal
from test_iot_ready_kit.resources.demo_data import ArtNetDemoData


def test_art_dmx_packet_equals_true():
    """ART NET DMX PACKET: Check if packet equals"""
    assert_equal(ArtNetDemoData.artnet_dmx_data(1), ArtNetDemoData.artnet_dmx_data(2))


def test_art_dmx_packet_equals_false():
    """ART NET DMX PACKET: Check if packet equals not"""
    dmx_packet_2 = ArtNetDemoData.artnet_dmx_data(2)
    dmx_packet_2.sequence = 2

    assert_not_equal(ArtNetDemoData.artnet_dmx_data(1), dmx_packet_2)
