from test_IoTReadyKit.resources.demo_carriage import DBModelsDemoDataCarriage

parts = DBModelsDemoDataCarriage.get_demo_parts_from_reference_sheet()
for part in parts:
    print(part.to_dict())
