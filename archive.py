from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import file, client, tools


QUERY = 'in:inbox is:read'
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'


## Auth
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))


## Messages
def archive(service):
    response = service.users().messages() \
               .list(userId='me', q=QUERY).execute()
    messages = []

    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        idx = response['nextPageToken']
        response = service.users().messages() \
                   .list(userId='me', q=QUERY, pageToken=idx) \
                   .execute()

        messages.extend(response['messages'])
        if len(messages) > 999:
            break

    ids = {
      'ids': [],
      'removeLabelIds': ['INBOX'],
    }

    ids['ids'].extend([str(d['id']) for d in messages])

    return service.users().messages() 
           .batchModify(userId='me', body=ids) \
           .execute()


for i in range(1000):
    print(archive(service))
