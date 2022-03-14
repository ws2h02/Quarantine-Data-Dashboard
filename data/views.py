from django.shortcuts import render
import requests
import json
import urllib.parse
from datetime import date, timedelta
# Create your views here.
from django.http import HttpResponse

def v3(request):
    connected = 0
    has_data = 0
    dayinpast = 0

    while True:
        days = date.today() - timedelta(days=dayinpast)
        strdate = days.strftime("%d/%m/%Y")
        r1 = {  "resource": "http://www.chp.gov.hk/files/misc/occupancy_of_quarantine_centres_eng.csv",
                "format": "json",
                "filters": [[1,"eq",[strdate]]]
            }

        r2 = {  "resource": "http://www.chp.gov.hk/files/misc/no_of_confines_by_types_in_quarantine_centres_eng.csv",
                "format": "json",
                "filters": [[1,"eq",[strdate]]]
            }

        q1 = json.dumps(r1)
        q2 = json.dumps(r2)
        url1 = "https://api.data.gov.hk/v2/filter?q=" + urllib.parse.quote(q1)
        url2 = "https://api.data.gov.hk/v2/filter?q=" + urllib.parse.quote(q2)
        j1 = requests.get(url1)
        j2 = requests.get(url2)
        if j1.status_code == 200 and j2.status_code == 200:
            connected = 1
        dayinpast += 1
        if j1.text != '[]' and j2.text != '[]':
            has_data = 1
            break
        if dayinpast > 7:
            break
    API1 = j1.json()
    API2 = j2.json()

    units_in_use = 0
    units_available = 0
    availability = []
    names = []
    units = []
    person_in_use = 0
    for x in API1:
        units_in_use += x['Current unit in use']
        units_available += x['Ready to be used (unit)']
        person_in_use += x['Current person in use']
        availability.append(x['Ready to be used (unit)'] / x['Capacity (unit)'])
        names.append(x['Quarantine centres'])
        units.append(x['Ready to be used (unit)'])
    non_close_contacts = API2[0]['Current number of non-close contacts']
    persons_quarantined = API2[0]['Current number of close contacts of confirmed cases'] + non_close_contacts
    if persons_quarantined == person_in_use:
        consistent = True
    else:
        consistent = False

    centres = sorted(zip(availability, names, units), reverse=True)[:3]
    context = {"connected": connected, 
               "has_data": has_data, 
               "data": { "date": strdate,
                         "units_in_use": units_in_use,
                         "units_available": units_available,
                         "persons_quarantined": persons_quarantined,
                         "non_close_contacts": non_close_contacts,
                         'count_consistent': consistent
                        },
               "centres": [{"name": centres[0][1],
                            "units": centres[0][2]},
                           {"name": centres[1][1],
                            "units": centres[1][2]},
                           {"name": centres[2][1],
                            "units": centres[2][2]}
                           ]
               }

    return render(request, 'dashboard3.html', context=context)

