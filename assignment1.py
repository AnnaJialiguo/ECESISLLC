import pandas as pd
import datetime

def is_nrec_holiday(date):
    nerc_holidays = {
        (1, 1),   # New Year's Day
        (5, 27),  # Memorial Day (last Monday in May)
        (7, 4),   # Independence Day
        (9, 2),   # Labor Day (first Monday in September)
        (11, 28), # Thanksgiving Day (fourth Thursday in November)
        (12, 25)  # Christmas Day
    }
    return (date.month, date.day) in nerc_holidays

def get_hours(iso, peak_type, period):
    # Define peak type
    peak_hours = {
        "onpeak": list(range(7, 23)),
        "offpeak": [h for h in range(24) if h not in range(7, 23)],
        "flat": list(range(24)),
        "2x16H": list(range(7, 23)),
        "7x8": [h for h in range(24) if h not in range(7, 23)]
    }
    # Define period
    if period.endswith("A"): #Annually
        start_date = datetime.datetime.strptime(period[:-1] + "-01-01", "%Y-%m-%d")
        end_date = datetime.datetime.strptime(period[:-1] + "-12-31", "%Y-%m-%d")
    elif period[-2]=="Q": #Quartly
        year, quarter = period[:-2], period[-2:]
        if quarter == "Q1":
            start_date = datetime.datetime.strptime(year + "-01-01", "%Y-%m-%d")
            end_date = datetime.datetime.strptime(year + "-03-31", "%Y-%m-%d")
        elif quarter == "Q2":
            start_date = datetime.datetime.strptime(year + "-04-01", "%Y-%m-%d")
            end_date = datetime.datetime.strptime(year + "-06-30", "%Y-%m-%d")
        elif quarter == "Q3":
            start_date = datetime.datetime.strptime(year + "-07-01", "%Y-%m-%d")
            end_date = datetime.datetime.strptime(year + "-09-30", "%Y-%m-%d")
        elif quarter == "Q4":
            start_date = datetime.datetime.strptime(year + "-10-01", "%Y-%m-%d")
            end_date = datetime.datetime.strptime(year + "-12-31", "%Y-%m-%d")
    elif len(period) == 7:  # Monthly
        year, monthtxt = period[:-3], period[-3:]
        month = datetime.datetime.strptime(monthtxt, "%B").strftime("%m")
        start_date = datetime.datetime.strptime(year+ "-"+month + "-01", "%Y-%m-%d")
        end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    else:  # Daily
        start_date = datetime.datetime.strptime(period, "%Y-%m-%d")
        end_date = start_date

    num_hours = 0
    current_date = start_date
    while current_date <= end_date:
        if peak_type == "onpeak":
            if current_date.weekday() < 5 and not is_nrec_holiday(current_date):  # Monday to Friday, non-NERC holiday
                num_hours += len(peak_hours["onpeak"])
        elif peak_type == "offpeak":
            if current_date.weekday() >= 5 or is_nrec_holiday(current_date):  # Weekends and NERC holidays
                num_hours += 24
            else:
                num_hours += len(peak_hours["offpeak"])
        elif peak_type == "flat":
            num_hours += 24
        elif peak_type == "2x16H":
            if current_date.weekday() >= 5 or is_nrec_holiday(current_date):  # Weekends and NERC holidays
                num_hours += len(peak_hours["2x16H"])
        elif peak_type == "7x8":
            if current_date.weekday() < 5 and not is_nrec_holiday(current_date):  # Monday to Friday, non-NERC holiday
                num_hours += len(peak_hours["7x8"])
        current_date += datetime.timedelta(days=1)

    return {
        "iso": iso,
        "peak_type": peak_type.upper(),
        "startdate": start_date.strftime("%Y-%m-%d"),
        "enddate": end_date.strftime("%Y-%m-%d"),
        "num_hours": num_hours
    }

# Sample run
df = pd.read_csv('C:/Users/Lenovo/Downloads/EGPS_PowerCalendar.csv')
results = get_hours("ERCOT", "onpeak", "2019May")
print(results)



