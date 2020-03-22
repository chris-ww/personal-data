import pandas as pd 
import datetime
import sys
sys.path.append('sites/tracker')
from packages.importer import collect_sleep,collect_activity,fitbit_client,collect_heart,collect_calendar,collect_location

#Dates in multiple formats 
yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
yesterday3 = datetime.datetime.today() - datetime.timedelta(hours=40)
yesterday3=yesterday3.isoformat()+'Z'
today = str(datetime.datetime.now().strftime("%Y%m%d"))
today2 = str((datetime.datetime.now() - datetime.timedelta(days=0)).strftime("%Y-%m-%d"))
today3 = datetime.datetime.today() - datetime.timedelta(hours=16)
today3=today3.isoformat()+'Z'

#using credentials saved on computer
codes=pd.read_csv("code.csv")
client=fitbit_client(codes.id[0],codes.secret[0])

#collecting data
heartdf=collect_heart(yesterday2,client)
sleepdf=collect_sleep(today2,client)
activitydf=collect_activity(yesterday2,client)
calendardf=collect_calendar(yesterday3,today3)
locdf=collect_location("sites/tracker/data/MAR2020LOC.json)

#saving data in csv
heartdf.to_csv('data/heart.csv',mode='a', header=True, index=False)
sleepdf.to_csv('data/sleep.csv', mode='a', header=False,index=False)
activitydf.to_csv('data/activity.csv', mode='a', header=True,index=False)
calendardf.to_csv('data/calendar.csv', mode='a', header=True,index=False)
locdf.to_csv('data/location.csv', mode='a', header=True,index=False)