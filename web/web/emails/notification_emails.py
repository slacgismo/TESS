# from web.models.alert import Alert
#from sqlalchemy import event
# def send_message(service, user_id, message):
#   '''Send an email message.

#   Args:
#     service: Authorized Gmail API service instance.
#     user_id: User's email address. The special value "me"
#     can be used to indicate the authenticated user.
#     message: Message to be sent.

#   Returns:
#     Sent Message.

#   Source:
#     https://developers.google.com/gmail/api/guides/sending?hl=en_US
#   '''
#   try:
#     message = (service.users().messages().send(userId=user_id, body=message)
#                .execute())
#     print('Message Id: %s' % message['id'])
#     return message
#   except errors.HttpError as error:
#     print('An error occurred: %s' % error)
# @event.listens_for(Alert, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     '''listens for a new alert event inserted to database,
#         sends notification emails if in database'''
        
#     # Query all notifications that are active for the alert type
#     notifications = Notification.query.filter(Notification.alert_type_id==target.alert_type_id, Notification.is_active==True).all()

#     # Check if notifications is empty
#     if notifications == []:
#         return None
        
#     # Create appropriate notification message
#     if target.alert_type.name.value == 'Resource':
#         message = 'TESS is showing "battery" resource depleted.'
    
#     elif target.alert_type.name.value == 'Telecomm':
#         message = 'TESS is observing a telecomm alert.'
    
#     elif target.alert_type.name.value == 'Price':
#         message = f'TESS is observing a price alert at ${target.alert_type.limit}/MW.'

#     elif target.alert_type.name.value == 'Load Yellow' \
#         or target.alert_type.name.value == 'Load Red':
#         message = f'TESS {target.alert_type.name.value} alert: {target.context} {target.context_id} is above {target.alert_type.limit}% capacity at {target.created_at}.'
    
#     elif target.alert_type.name.value == 'Price Yellow' \
#         or target.alert_type.name.value == 'Price Red':
#         message = f'TESS {target.alert_type.name.value} alert: {target.context} {target.context_id} is above {target.alert_type.limit}% of the alert price at {target.created_at}.'
    
#     elif target.alert_type.name.value == 'Import Capacity':
#         message = f'TESS System alert: {target.context} {target.context_id} is above {target.alert_type.limit} kW import capacity at {target.created_at}.'
    
#     elif target.alert_type.name.value == 'Export Capacity':
#          message = f'TESS System alert: {target.context} {target.context_id} is above {target.alert_type.limit} kW export capacity at {target.created_at}.'

#     # Send email notification for each notification
#     for notification in notifications:
#         send_message(service, notification.email, message)