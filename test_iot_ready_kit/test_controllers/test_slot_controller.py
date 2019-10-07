from unittest.mock import patch
from nose.tools import assert_equal
import configparser
from iot_ready_kit.controllers.slot_controller import SlotController
from test_iot_ready_kit.resources.demo_data import DBModelsDemoData, IniDemoData


def fake_check_if_config_has_changed(self):
    return True


def fake_remove_unnecessary_slots_modules(self):
    pass


def setup_carriage_configparser():
    carriage_config = configparser.ConfigParser()
    carriage_config.read_dict(IniDemoData.ini_get_carriage_ini(1))
    return carriage_config


def setup_irk_configparser():
    irk_config = configparser.ConfigParser()
    irk_config.read_dict(IniDemoData.ini_get_iot_ready_kit_ini(1))
    return irk_config


@patch('iot_ready_kit.common.RestClient.RestClient')
@patch('iot_ready_kit.common.ConfigManager.ConfigManager')
@patch.object(SlotController, '_check_if_config_has_changed', fake_check_if_config_has_changed)
@patch.object(SlotController, '_remove_unnecessary_slots_modules', fake_remove_unnecessary_slots_modules)
def test_slot_controller_prepare_database_true(mock_rest, mock_config_manager):
    """SLOT CONTROLLER: Check if prepare_database returns true"""

    # Patching of ConfigManager is needed, otherwise the __init__ of SlotController will fail
    # Prepare mock_rest with return values
    mock_rest.get_module.return_value = None
    mock_rest.create_module.return_value = 201
    mock_rest.get_slot_with_name.return_value = None
    mock_rest.create_slot.return_value = 201

    # Init SlotController and inject mocks
    slot_controller = SlotController()
    slot_controller.rest_client = mock_rest
    slot_controller.carriage_config = setup_carriage_configparser()
    slot_controller.irk_config = setup_irk_configparser()

    # Check if return value is true
    ret = slot_controller.prepare_database()

    assert_equal(ret, True)


@patch('iot_ready_kit.common.RestClient.RestClient')
@patch('iot_ready_kit.common.ConfigManager.ConfigManager')
@patch.object(SlotController, '_check_if_config_has_changed', fake_check_if_config_has_changed)
@patch.object(SlotController, '_remove_unnecessary_slots_modules', fake_remove_unnecessary_slots_modules)
def test_slot_controller_prepare_database_false(mock_rest, config_manager):
    """SLOT CONTROLLER: Check if prepare_database returns false"""

    # Patching of ConfigManager is needed, otherwise the __init__ of SlotController will fail
    # Prepare mock_rest with return values
    mock_rest.get_module.return_value = None
    mock_rest.create_module.return_value = 404
    mock_rest.get_slot_with_name.return_value = None
    mock_rest.create_slot.return_value = 201
    mock_rest.get_carriage.return_value = DBModelsDemoData.dbmodels_get_carriage(1)

    # Init SlotController and inject mocks
    slot_controller = SlotController()
    slot_controller.rest_client = mock_rest
    slot_controller.carriage_config = setup_carriage_configparser()
    slot_controller.irk_config = setup_irk_configparser()

    # Check if return value is false
    ret = slot_controller.prepare_database()

    assert_equal(ret, False)


@patch('iot_ready_kit.common.RestClient.RestClient')
@patch('iot_ready_kit.common.ConfigManager.ConfigManager')
@patch.object(SlotController, '_check_if_config_has_changed', fake_check_if_config_has_changed)
@patch.object(SlotController, '_remove_unnecessary_slots_modules', fake_remove_unnecessary_slots_modules)
def test_slot_controller_prepare_database_rest_module_update_ok(mock_rest, config_manager):
    """SLOT CONTROLLER: Check if rest update_module in prepare_database is called 2 times"""
    # Patching of ConfigManager is needed, otherwise the __init__ of SlotController will fail
    # Prepare mock_rest with return values
    mock_rest.get_module.side_effect = [DBModelsDemoData.dbmodels_get_module(1),
                                        DBModelsDemoData.dbmodels_get_module(2)]
    mock_rest.update_module.return_value = 200
    mock_rest.get_slot_with_name.return_value = None
    mock_rest.create_slot.return_value = 201

    # Init SlotController and inject mocks
    slot_controller = SlotController()
    slot_controller.rest_client = mock_rest
    slot_controller.carriage_config = setup_carriage_configparser()
    slot_controller.irk_config = setup_irk_configparser()

    # Check if update_module is called 2 times
    slot_controller.prepare_database()
    update_module_call_count = mock_rest.update_module.call_count

    assert_equal(update_module_call_count, 2)


@patch('iot_ready_kit.common.RestClient.RestClient')
@patch('iot_ready_kit.common.ConfigManager.ConfigManager')
@patch.object(SlotController, '_check_if_config_has_changed', fake_check_if_config_has_changed)
@patch.object(SlotController, '_remove_unnecessary_slots_modules', fake_remove_unnecessary_slots_modules)
def test_slot_controller_prepare_database_rest_slot_update_ok(mock_rest, config_manager):
    """SLOT CONTROLLER: Check if rest update_slot in prepare_database is called 2 times"""
    # Patching of ConfigManager is needed, otherwise the __init__ of SlotController will fail
    # Prepare mock_rest with return values
    mock_rest.get_module.return_value = None
    mock_rest.update_module.return_value = 201
    mock_rest.get_slot_with_name.side_effect = [DBModelsDemoData.dbmodels_get_slot(1),
                                                DBModelsDemoData.dbmodels_get_slot(1),
                                                DBModelsDemoData.dbmodels_get_slot(2),
                                                DBModelsDemoData.dbmodels_get_slot(2),
                                                None, None, None, None, None, None, None, None]
    mock_rest.create_slot.return_value = 200
    mock_rest.get_carriage.return_value = DBModelsDemoData.dbmodels_get_carriage(1)

    # Init SlotController and inject mocks
    slot_controller = SlotController()
    slot_controller.rest_client = mock_rest
    slot_controller.carriage_config = setup_carriage_configparser()
    slot_controller.irk_config = setup_irk_configparser()

    # Check if update_slot is called 2 times
    slot_controller.prepare_database()

    assert_equal(mock_rest.update_slot.call_count, 2)
