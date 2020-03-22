from __future__ import print_function
import fitbit
import pandas as pd 
from fitbit import gather_keys_oauth2 as Oauth2
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



def fitbit_client(id,secret):
    #Accepts id, secret credentials
    #uses id, secret to log into fitbit client
    #retrieves access token,refresh token
    #returns client

    server = Oauth2.OAuth2Server(id, secret)
    server.browser_authorize()
    accesstoken = str(server.fitbit.client.session.token['access_token'])
    refreshtoken = str(server.fitbit.client.session.token['refresh_token'])
    client = fitbit.Fitbit(id, secret, oauth2=True, access_token=accesstoken, refresh_token=refreshtoken)
    return client
    
def collect_heart(date,client):
    #Accepts date to access, fitbit client
    #returns time and heart rate from day requested in pandas dataframe

    time_list = []
    val_list = []
    heart = client.intraday_time_series('activities/heart', base_date=date, detail_level='1min')
    for i in heart['activities-heart-intraday']['dataset']:
        val_list.append(i['value'])
        time_list.append(i['time'])
    heartdf = pd.DataFrame({'Date':date,'Heart Rate':val_list,'Time':time_list})
    return heartdf
    

def collect_sleep(date,client):      
    #Accepts date to access, fitbit client
    #returns summary sleep data from day requested in pandas dataframe
     
    sleep = client.sleep(date=date)['sleep'][0]
    sleepdf = pd.DataFrame({'Date':sleep['dateOfSleep'],
               'MainSleep':sleep['isMainSleep'],
               'Efficiency':sleep['efficiency'],
               'Duration':sleep['duration'],
               'Minutes Asleep':sleep['minutesAsleep'],
               'Minutes Awake':sleep['minutesAwake'],
               'Awakenings':sleep['awakeCount'],
               'Restless Count':sleep['restlessCount'],
               'Restless Duration':sleep['restlessDuration'],
               'Time in Bed':sleep['timeInBed'],'start':sleep['startTime'],'end':sleep['endTime']
                        } ,index=[0])
    return sleepdf

def collect_activity(date,client):
    #Accepts date to access, fitbit client
    #returns summary activity from day requested in pandas dataframe

    activity = client.activities(date=date)['summary']
    activitydf = pd.DataFrame({'Date':date,
               'Activity Calories':activity['activityCalories'],
               'Calories Out':activity['caloriesOut'],
               'Steps':activity['steps'],
               'floors':activity['floors'],
               'very active minutes':activity['veryActiveMinutes'],
               'fairly active minutes':activity['fairlyActiveMinutes'],
               'lightly active minutes':activity['lightlyActiveMinutes'],
               'sedentary minutes':activity['sedentaryMinutes'] } ,index=[0])
    return activitydf
    
def collect_calendar(date1,date2):
    #Accepts start date, end date
    #Uses code google https://developers.google.com/calendar/quickstart/python to login to api
    #uses and stores credentials as token on computer
    #returns list of calendar events in pandas dataframe

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
    
    events_result = service.events().list(calendarId='primary', timeMin=date1,timeMax=date2,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    #returns list of calendar events in pandas dataframe
    start_list = []
    end_list = []
    name_list=[]
    desc_list=[]
    for i in events:
        start_list.append(i['start']['dateTime'])
        end_list.append(i['end']['dateTime'])
        name_list.append(i['summary'])
        #desc_list.append(i['description'])
    eventdf=pd.DataFrame({'Date':date1,
                    'start':start_list,
                    'end':end_list,
                    'event':name_list})
    return eventdf

def collect_location(file):
    #Accepts file name
    #Opens Json file and extracts locations,activities and times
    #returns pandas dataframe
  
    with open(file) as f:
        data = json.load(f)
        event_list = []
        start_list=[]
        end_list=[]
        for i in data['timelineObjects']:      
            if 'activitySegment' in i:
                event_list.append(i['activitySegment']['activityType'])
                start_list.append(i['activitySegment']['duration']['startTimestampMs'])
                end_list.append(i['activitySegment']['duration']['endTimestampMs'])
            if 'placeVisit' in i:     
                event_list.append(i['placeVisit']['location']['name'])
                start_list.append(i['placeVisit']['duration']['startTimestampMs'])
                end_list.append(i['placeVisit']['duration']['endTimestampMs'])
            
        locdf = pd.DataFrame({'start':start_list,'end':end_list,'location':event_list}) 
        return locdf        
    