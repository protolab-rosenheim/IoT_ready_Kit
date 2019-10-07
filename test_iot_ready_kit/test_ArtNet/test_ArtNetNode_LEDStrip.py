from unittest.mock import patch
import copy
from nose.tools import assert_equal, assert_not_equal
from iot_ready_kit.ArtNet.ArtNetNode import LEDStrip


def test_led_strip():
    """LED STRIP: Check if led_strip equal returns True"""
    led_strip_1 = LEDStrip(20)
    led_strip_1.led_strip[0].set_color('green')
    led_strip_2 = copy.deepcopy(led_strip_1)

    assert_equal(led_strip_1, led_strip_2)


def test_led_strip_equal_false():
    """LED STRIP: Check if led_strip equal returns False"""
    led_strip_1 = LEDStrip(20)
    led_strip_2 = LEDStrip(20)
    led_strip_1.led_strip[0].set_color('green')
    led_strip_2.led_strip[0].set_color('green')
    led_strip_2.led_strip[0].set_color('red')

    assert_not_equal(led_strip_1, led_strip_2)
