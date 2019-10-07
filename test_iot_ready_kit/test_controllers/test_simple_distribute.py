from unittest.mock import patch
from nose.tools import assert_equal
from iot_ready_kit.controllers.simple_distribute import SimpleDistribute
from test_iot_ready_kit.resources.demo_data import DBModelsDemoData


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_simple_distribute_return_booked_slot_ok(mock_rest):
    """SIMPLE DISTRIBUTE: Check if returned slot is ok"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(1)
    mock_rest.get_suitable_slots.return_value = DBModelsDemoData.dbmodels_get_slot_list(1)
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 200
    slot = DBModelsDemoData.dbmodels_get_slot_list(1)[-1]

    simple_distribute = SimpleDistribute(mock_rest)
    booked_slot = simple_distribute.distribute_and_book(11)

    assert_equal(booked_slot, slot.slot_name)


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_simple_distribute_update_slot_ok(mock_rest):
    """SIMPLE DISTRIBUTE: Check if update_slot call is ok"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(1)
    mock_rest.get_suitable_slots.return_value = DBModelsDemoData.dbmodels_get_slot_list(1)
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 200
    slot = DBModelsDemoData.dbmodels_get_slot_list(1)[-1]

    simple_distribute = SimpleDistribute(mock_rest)
    simple_distribute.distribute_and_book(11)

    updated_slot = mock_rest.update_slot.mock_calls[0][1][0]
    slot.part_number = DBModelsDemoData.dbmodels_get_part(1).part_number

    assert_equal(updated_slot, slot)


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_simple_distribute_update_part_ok(mock_rest):
    """SIMPLE DISTRIBUTE: Check if update_slot call is ok 2"""
    part = DBModelsDemoData.dbmodels_get_part(1)
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(1)
    mock_rest.get_suitable_slots.return_value = DBModelsDemoData.dbmodels_get_slot_list(1)
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 200

    simple_distribute = SimpleDistribute(mock_rest)
    simple_distribute.distribute_and_book(11)

    updated_part = mock_rest.update_part.mock_calls[0][1][0]
    part.status = 'onboard'

    assert_equal(updated_part, part)


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_simple_distribute_find_slot_not_found(mock_rest):
    """SIMPLE DISTRIBUTE: Check if returned value is '' if part is to big for a slot"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(2)
    mock_rest.get_suitable_slots.return_value = None
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 200

    simple_distribute = SimpleDistribute(mock_rest)
    booked_slot = simple_distribute.distribute_and_book(12)

    assert_equal(booked_slot, '')


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_simple_distribute_reaction_on_http_status_code_404_update_slot(mock_rest):
    """SIMPLE DISTRIBUTE: Check if returned slot is '' if update_slot return value is 404"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(2)
    mock_rest.get_suitable_slots.return_value = DBModelsDemoData.dbmodels_get_slot_list(1)
    mock_rest.update_slot.return_value = 404
    mock_rest.update_part.return_value = 200

    simple_distribute = SimpleDistribute(mock_rest)
    booked_slot = simple_distribute.distribute_and_book(12)

    assert_equal(booked_slot, '')


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_simple_distribute_reaction_on_http_status_code_404_update_part(mock_rest):
    """SIMPLE DISTRIBUTE: Check if returned slot is '' if update_part return value is 404"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(2)
    mock_rest.get_suitable_slots.return_value = DBModelsDemoData.dbmodels_get_slot_list(1)
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 404

    simple_distribute = SimpleDistribute(mock_rest)
    booked_slot = simple_distribute.distribute_and_book(12)

    assert_equal(booked_slot, '')
