from packages.importer import collect_fitbit_trigger,collect_rescue_trigger
from datetime import timedelta,datetime

"""
imports fitbit and rescuetime data for today"
"""

collect_rescue_trigger()
collect_fitbit_trigger()
