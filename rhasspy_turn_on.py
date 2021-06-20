# rhasspy_turn_on.py
# hass.states.get(entity_id): https://www.home-assistant.io/docs/configuration/state_object/
# entity name convention: 
#    1) domain.device_room_floor (the floor part is optional if there is only one floor), e.g., light.night_light_master_room_second_floor
#    2) if there is only one such device, the room and floor part can be omitted, e.g., switch.tv if there is only one TV
entity_ids = hass.states.entity_ids()
message = data.get("message")
event_type = data.get('event_type')
#message = message.get("_intent").get("input")

# find the area of the site
site_id_to_area = {'rpizero_master': 'master_room', 'rpizero_study': 'study_room'}
site_area = site_id_to_area.get(message.get('_intent').get('siteId'))
    

# get area of the device
slots = message.get("_intent").get("slots")
area = ""
dev_name = ""
if slots is not None:
    # get area and entity type
    room = ""
    floor = ""
    for s in slots:
        e = s.get("entity")
        if e == 'room':
            room = s.get('rawValue')
        if e == 'floor':
            floor = s.get('rawValue')
        if e == 'device':
            dev_name = s.get('rawValue')
    area = room + ' ' + floor
    area = area.strip()
    area = area.replace(' ', '_')
    

# full device name
full_dev_name = dev_name
if area is not None and area != '':
    full_dev_name = dev_name + "_" + area   

    
# find the action to take: on or off
action = None
if event_type == 'rhasspy_turn_on':
    action = 'turn_on'
elif event_type == 'rhasspy_turn_off':
    action = 'turn_off'

# handle the intent    
if action is not None:   

    domain = None

    # try to identify the related entity
    # first, search the full name
    for ent in entity_ids:
        b = hass.states.get(ent).object_id
        if b is not None and b == full_dev_name:
            domain = hass.states.get(ent).domain
            break
    
    # if not found and area is None and the area is not None, then try  domain + device name + area of site ID
    if domain is None and area == '' and site_area is not None:
        full_dev_name = dev_name + '_' + site_area
        for ent in entity_ids:
            b = hass.states.get(ent).object_id
            if b is not None and b == full_dev_name:
                domain = hass.states.get(ent).domain
                break
    
    if domain is not None:
        service_data = {"entity_id": ent}
        hass.services.call(domain, action, service_data, False)
    else:
        service_data = {"title": 'Unrecognized Entity', "message": full_dev_name + " is not recognized!"}
        hass.services.call("persistent_notification", "create", service_data, False)
    
else:
    # unsupported action
    service_data = {"title": 'Unsupported Intent', "message": event_type + " is not supported yet!"}
    hass.services.call("persistent_notification", "create", service_data, False)
        
        
        
        
        
        
        
