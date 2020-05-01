# personal-data
code used to gather/analyze data from fitbit, google calendar,rescuetime, DoItNowRPG and google location history.
Need to gather own credentials to use.

collect_fitbit.py
    Airflow dag to collect fitbit data daily
    
collect_rescue.py
    Airflow dag to collect rescuetime data daily
    
importer.py
    contains functions to import data from fitbit/google/rescuetime/DoItNow
    fitbit_client
        accepts id and code credentials
        returns client
    collect_heart, collect_sleep,collect_activity,collect_body,collect_food
        accepts date, client
        returns dataframe with fitbit data
    collect_calendar
        accepts start/end dates
        returns dataframe with google calendar events
    collect_location
        accepts location of google location history json
        returns dataframe with location history
    create_connection
        accepts database file
        returns connection to database
    select_all_tasks
        accepts database connection
        returns tasks from DoItNow database
    collect_fitbit_day,collect_rescue
        accepts airflow keys/arguments(kwargs)
        collects data from api for previous day
        loads in database personal_data.db
    collect_fitbit_trigger,collect_rescue_trigger
        collects todays api data into personal_data_trigger.db
    Rescue_activities
        accepts date, api url
        returns api data from rescuetime for date
        
plot.R
    collects and from database
    cleans/manipulates data
    plots bullet graphs/line graphs
    
