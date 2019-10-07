import logging

from iot_ready_kit.common.db_client import DBClient


class FitBestDistribute:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def distribute_and_book(self, part_number):
        part = DBClient.get_part(part_number)
        part_space = float(part.finished_length * part.finished_width)
        booked_slot = ''

        if part:
            # Get suitable slots
            slots = DBClient.get_suitable_slots(part.finished_length, part.finished_width, part.finished_thickness)
            # Get suitable slots with width and length swapped
            slots.extend(DBClient.get_suitable_slots(part.finished_width, part.finished_length, part.finished_thickness))
            slots_calculated = self.calculate_space(slots)

            if slots_calculated:
                # Finds slot with lowest wasted space, if there are multiple similar slots get the first one
                best_slot = slots_calculated[min(slots_calculated, key=lambda x: abs(x - part_space))][0]

                best_slot.part_number = part.part_number
                status_slot = DBClient.upd_slot(best_slot)
                part.status = 'onboard'
                status_part = DBClient.upd_part(part)

                if status_slot and status_part:
                    self.logger.info('Successfully booked part {}'.format(part.part_number))
                    booked_slot = best_slot.slot_name
                else:
                    self.logger.error('DB client error while booking part {} with slot status {} and part status {}'
                                      .format(part.part_number, status_slot, status_part))

        else:
            self.logger.warning('Could not find part with part number {}'.format(part_number))

        return booked_slot

    @staticmethod
    def calculate_space(slots):
        slots_dict = {}
        for slot in slots:
            space = float(slot.max_length * slot.max_width)
            if slots_dict.get(space):
                slots_dict[space].append(slot)
            else:
                slots_dict[space] = [slot]

        return slots_dict

    @staticmethod
    def strategy():
        return 'Complex distribute v 1.0'
