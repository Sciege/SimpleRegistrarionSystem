import requests

server_url = 'http://127.0.0.1:5000/api'

def create_event(event_name, event_date):
    event = {'name': event_name, 'date': event_date}
    response = requests.post(f'{server_url}/events', json=event)
    print(response.json())

def list_events():
    response = requests.get(f'{server_url}/events')
    events = response.json()
    print('\nEvents:')
    for i, event in enumerate(events):
        print(f'{event["id"]}: {event["name"]} on {event["date"]}')
    return events

def register_student(event_id, student_name):
    student = {'name': student_name}
    response = requests.post(f'{server_url}/events/{event_id}/register', json=student)
    print(response.json())

def list_registrations(event_id):
    response = requests.get(f'{server_url}/events/{event_id}/registrations')
    print(response.json())

if __name__ == '__main__':
    # Example workflow
    create_event('Hackathon', '2024-09-15')
    create_event('Science Fair', '2024-10-20')

    events = list_events()

    if events:
        register_student(events[0]['id'], 'Alice')
        register_student(events[1]['id'], 'Bob')
        list_registrations(events[0]['id'])
        list_registrations(events[1]['id'])