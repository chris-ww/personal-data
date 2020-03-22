# personal-data
code used to gather/analyze data from fitbit, google calendar and google location history.
Need to gather own credentials to use.

main.py
    uses importer.py functions to collect data, save as csv

importer.py
    contains functions to import data from fitbit/google
    fitbit_client
        accepts id and code credentials
        returns client
    collect_heart, collect_sleep,collect_activity
        accepts date, client
        returns dataframe with fitbit data
    collect_calendar
        accepts start/end dates
        returns dataframe with google calendar events
    collect_location
        accepts location of google location history json
        returns dataframe with location history
        
plot.R
    collects and from csv files
    cleans data
    combines into schedule figure in gantt chart
    
