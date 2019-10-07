import logging

from iot_ready_kit.common.db_client import DBClient


class SimpleDistribute:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def distribute_and_book(self, part_number):
        part = DBClient.get_part(part_number)
        booked_slot = ''

        if part:
            slots = DBClient.get_suitable_slots(part.finished_length, part.finished_width, part.finished_thickness)
            if slots:
                slot = slots.pop()
                slot.part_number = part.part_number
                status_slot = DBClient.upd_slot(slot)
                part.status = 'onboard'
                status_part = DBClient.upd_part(part)

                if status_slot and status_part:
                    self.logger.info('Successfully booked part {}'.format(part.part_number))
                    booked_slot = slot.slot_name
                else:
                    self.logger.error('DB client error while booking part {} with slot status {} and part status {}'
                                      .format(part.part_number, status_slot, status_part))

        else:
            self.logger.warning('Could not find part with part number  {}'.format(part_number))

        return booked_slot

    @staticmethod
    def strategy():
        return 'Simple distribute v 1.0'
