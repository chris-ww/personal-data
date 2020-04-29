from __future__ import print_function
import fitbit
import pandas as pd 
from fitbit import gather_keys_oauth2 as Oauth2
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import sqlite3
from sqlite3 import Error
import config
import requests
from datetime import timedelta,datetime


def collect_fitbit_day(**kwargs):
    """
    Collects previous days data from fitbit api and stores it in database: personal_data.db
    input key/arguments from airflown contect
    """
    date=str((kwargs['execution_date']-timedelta(days=1)).strftime("%Y-%m-%d"))
    conn = sqlite3.connect('personal_data.db')
    client=fitbit_client(config.fitbit['id'],config.fitbit['secret'])
    bodydf=collect_body(date,client)
    fooddf,mealsdf=collect_food(date,client)
    heartdf=collect_heart(date,client)
    sleepdf=collect_sleep(date,client)
    activitydf=collect_activity(date,client)
    sleepdf.to_sql('sleep', con=conn, index=False,if_exists='append')
    activitydf.to_sql('activty', con=conn, index=False,if_exists='append')
    fooddf.to_sql('food', con=conn, index=False,if_exists='append')
    mealsdf.to_sql('meals', con=conn, index=False,if_exists='append')
    bodydf.to_sql('body', con=conn, index=False,if_exists='append')
    heartdf.to_sql('heart', con=conn, index=False,if_exists='append')
    conn.close()

def collect_fitbit_trigger():
    """
    Collects todays data from fitbit api and stores it in database: personal_data_trigger.db
    """
    date=str(datetime.now().strftime("%Y-%m-%d"))
    conn = sqlite3.connect('personal_data_trigger.db')
    client=fitbit_client(config.fitbit['id'],config.fitbit['secret'])
    bodydf=collect_body(date,client)
    fooddf,mealsdf=collect_food(date,client)
    heartdf=collect_heart(date,client)
    sleepdf=collect_sleep(date,client)
    activitydf=collect_activity(date,client)
    sleepdf.to_sql('sleep', con=conn, index=False,if_exists='replace')
    activitydf.to_sql('activty', con=conn, index=False,if_exists='replace')
    mealsdf.to_sql('meals', con=conn, index=False,if_exists='replace')
    conn.close()

def collect_rescue(**kwargs):
    """
    Collects previous days data from rescuetime api and stores it in database: personal_data.db
    kwargs key/arguments from airflown contect
    """
    date=str((kwargs['execution_date']-timedelta(days=1)).strftime("%Y-%m-%d"))
    url='https://www.rescuetime.com/anapi/data?key=' + config.rescue['secret']
    rescuedb=rescue_activities(date,url)
    conn = sqlite3.connect('personal_data.db')
    rescuedb.to_sql('rescue', con=conn, index=False,if_exists='append')
    conn.close()
    
def collect_rescue_trigger():
    """
    Collects todays data from rescuetime api and stores it in database: personal_data_trigger.db
    """
    date=str(datetime.now().strftime("%Y-%m-%d"))
    url='https://www.rescuetime.com/anapi/data?key=' + config.rescue['secret']
    rescuedb=rescue_activities(date,url)
    conn = sqlite3.connect('personal_data_trigger.db')
    rescuedb.to_sql('rescue', con=conn, index=False,if_exists='replace')
    conn.close()

def rescue_activities(date,url):
    """
    Calls Resucuetime api
    date: date to collect_activity
    url: rescuetime url with key
    returns: pandas dataframe with rescuetime data
    """
    payload = {
        'perspective':'interval',
        'resolution_time': "day",
        'restrict_kind':'document',
        'restrict_begin': date,
        'restrict_end': date,
        'format':'json' #csv
    }
    dur_list = []
    prod_list = []
    type_list=[]
    name_list=[]
    desc_list=[]
    per_list=[]
    try: 
        r = requests.get(url, payload) 
        iter_result = r.json() 
    except: 
        print("Error collecting data for ")
    
    if len(iter_result) != 0:
         for i in iter_result['rows']:
            dur_list.append(i[1])
            per_list.append(i[2])
            name_list.append(i[3])
            desc_list.append(i[4])
            type_list.append(i[5])
            prod_list.append(i[6])
    else:
        print("Appears there is no RescueTime data")
        
    rescuedb=pd.DataFrame({"date":date,"period":per_list,"duration":dur_list,"program":name_list,"description":desc_list,"productive":prod_list,"category":type_list})
    return rescuedb

def fitbit_client(id,secret):
    """
    connects to fitbit api client
    id: user fitbit api id
    secret: firbit api password
    returns: fitbit client connection
    """
    server = Oauth2.OAuth2Server(id, secret)
    server.browser_authorize()
    accesstoken = str(server.fitbit.client.session.token['access_token'])
    refreshtoken = str(server.fitbit.client.session.token['refresh_token'])
    client = fitbit.Fitbit(id, secret, oauth2=True, access_token=accesstoken, refresh_token=refreshtoken)
    return client

def create_connection(db_file):
    """ 
    create a database connection to the SQLite database specified by the db_file
    db_file: database file
    return: Connection object or None
    from https://docs.python.org/2/library/sqlite3.html
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_all_tasks(conn):
    """
    Retrieve task data from database
    conn: connection to database
    return: dataframe with tasks
    """
    print(conn)
    cur = conn.cursor()
    cur.execute("SELECT task_title,execution_date,gained_xp,execution_note FROM task_executions")

    rows = cur.fetchall()
    task_list=[]
    time_list=[]
    xp_list=[]
    comment_list=[]
    for i in rows:
        task_list.append(i[0])
        time_list.append(i[1])
        xp_list.append(i[2])
        comment_list.append(i[3])
    taskdf=pd.DataFrame({"task":task_list,"time":time_list,"xp":xp_list,"comment":comment_list})
    return taskdf

def collect_heart(date,client):
    """
    Retrieve heart rate data from fitbit api
    date: date to collect
    client: connection to api
    return: pandas dataframe with heart data
    """
    time_list = []
    val_list = []
    heart = client.intraday_time_series('activities/heart', base_date=date, detail_level='1min')
    for i in heart['activities-heart-intraday']['dataset']:
        val_list.append(i['value'])
        time_list.append(i['time'])
    heartdf = pd.DataFrame({'Date':date,'Heart Rate':val_list,'Time':time_list})
    return heartdf
    
def collect_body(date,client):
    """
    Retrieve weight data from fitbit api
    date: date to collect
    client: connection to api
    return: pandas dataframe with weight data
    """
    time_list = []
    val_list = []
    body = client.body(date=date)
    bodydf = pd.DataFrame({'date':date,
                'weight':body['body']['weight'],
                'fat':body['body']['fat']
                },index=[0])
    return bodydf
    
def collect_sleep(date,client):   
    """
    Retrieve sleep rate data from fitbit api
    date: date to collect
    client: connection to api
    return: pandas dataframe with sleep data
    """        
    sleep = client.sleep(date=date)['sleep'][0]
    sleepdf = pd.DataFrame({'date':sleep['dateOfSleep'],
               'mainsleep':sleep['isMainSleep'],
               'efficiency':sleep['efficiency'],
               'duration':sleep['duration'],
               'minutes asleep':sleep['minutesAsleep'],
               'minutes awake':sleep['minutesAwake'],
               'awakenings':sleep['awakeCount'],
               'restless count':sleep['restlessCount'],
               'restless duration':sleep['restlessDuration'],
               'time in bed':sleep['timeInBed'],'start':sleep['startTime'],'end':sleep['endTime'],
               'fall asleep':sleep['minutesToFallAsleep']
                        } ,index=[0])
    return sleepdf

def collect_activity(date,client):
    """
    Retrieve activity rate data from fitbit api
    date: date to collect
    client: connection to api
    return: pandas dataframe with activity data
    """
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

def collect_food(date,client):
    """
    Retrieve diet rate data from fitbit api
    date: date to collect
    client: connection to api
    return: pandas dataframe with diet data
    """
    food=client.foods_log(date=date)
    name_list = []
    cal_list = []
    pro_list = []
    fat_list = []
    carbs_list = []
    fiber_list = []
    salt_list = []
    for i in food['foods']:
        name_list.append(i['loggedFood']['name'])
        cal_list.append(i['nutritionalValues']['calories'])
        pro_list.append(i['nutritionalValues']['protein'])
        carbs_list.append(i['nutritionalValues']['carbs'])
        fat_list.append(i['nutritionalValues']['fat'])
        fiber_list.append(i['nutritionalValues']['fiber'])
        salt_list.append(i['nutritionalValues']['sodium'])

    mealsdf = pd.DataFrame({'Date':date,'meal':name_list,'calories':cal_list,'protein':pro_list,'carbs':carbs_list,'fat':fat_list,'fiber':fiber_list,'sodium':salt_list})
    fooddf=pd.DataFrame({'Date':date,
                    'calories':food['summary']['calories'],
                    'protien':food['summary']['protein'],
                    'carbs':food['summary']['carbs'],
                    'fat':food['summary']['fat'],
                    'fiber':food['summary']['fiber'],
                    'sodium':food['summary']['sodium']},index=[0])
    return fooddf, mealsdf


def collect_location(file):
    """
    Retrieve location data from google personal data download
    file: location of file with data
    return: pandas dataframe with location data
    Not very interesting during pandemic
    """
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
    