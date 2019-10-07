from unittest.mock import patch
from nose.tools import assert_equal
from iot_ready_kit.controllers.fit_best_distribute import FitBestDistribute
from test_iot_ready_kit.resources.demo_data import DBModelsDemoData


def test_complex_distribute_calculate_space():
    """COMPLEX DISTRIBUTE: Check if calculated_space works correctly"""
    # Create slot_dict to compare to
    my_slot_dict = {36000.0: [DBModelsDemoData.dbmodels_get_slot(1), DBModelsDemoData.dbmodels_get_slot(2)],
                    300000.0: [DBModelsDemoData.dbmodels_get_slot(3), DBModelsDemoData.dbmodels_get_slot(4)],
                    400.0: [DBModelsDemoData.dbmodels_get_slot(5)]}
    complex_slot_dict = FitBestDistribute.calculate_space(DBModelsDemoData.dbmodels_get_slot_list(2))

    assert_equal(complex_slot_dict, my_slot_dict)


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_complex_distribute_return_booked_slot_ok(mock_rest):
    """COMPLEX DISTRIBUTE: Check if returned slot is the one with the smallest waste of space"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(3)
    mock_rest.get_suitable_slots.return_value = [DBModelsDemoData.dbmodels_get_slot(3),
                                                 DBModelsDemoData.dbmodels_get_slot(4),
                                                 DBModelsDemoData.dbmodels_get_slot(1),
                                                 DBModelsDemoData.dbmodels_get_slot(2)]
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 200

    fit_best_distribute = FitBestDistribute(mock_rest)

    assert_equal(fit_best_distribute.distribute_and_book(13), DBModelsDemoData.dbmodels_get_slot(1).slot_name)


@patch('iot_ready_kit.common.RestClient.RestClient')
def test_complex_distribute_no_slot_found(mock_rest):
    """COMPLEX DISTRIBUTE: Check if no slot is returned if part is to big for all slots"""
    mock_rest.get_part.return_value = DBModelsDemoData.dbmodels_get_part(3)
    mock_rest.get_suitable_slots.return_value = []
    mock_rest.update_slot.return_value = 200
    mock_rest.update_part.return_value = 200

    fit_best_distribute = FitBestDistribute(mock_rest)

    assert_equal(fit_best_distribute.distribute_and_book(13), '')
