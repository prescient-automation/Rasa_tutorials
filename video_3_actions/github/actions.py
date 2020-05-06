from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet




class ActionQuestion(Action):
    
    def name(self) -> Text:
        return "action_question"

    def run(self, dispatcher: CollectingDispatcher,

            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message('Found file')
        import pickle
        import os.path
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import logging

        logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)
    
        SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)


        
        service = build('drive', 'v3', credentials=creds)
        
        question = tracker.get_slot("document")
        dispatcher.utter_message('Sure, Here it is , please refer below documents for %s .  Hope it helps!' %(question))
        page_token = None
        while True:
            response = service.files().list(q='(fullText contains \'{0}\' and name contains \'{0}\')'.format(question, question),
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageSize = '1',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):

                dispatcher.utter_message('Found file: %s please visit the link https://drive.google.com/open?id=%s' % (file.get('name'), file.get('id')))

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break


        return []
        
        
         

