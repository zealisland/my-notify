import datetime
import re
import sys
import urllib.parse

from bs4 import BeautifulSoup

import requests as requests


def check_availability(zip_codes, date_ranges, radius=50, vac_name="Pfizer"):
    found = False

    for zip_ in zip_codes:
        delta = date_ranges[1] - date_ranges[0]
        for i in range(delta.days + 1):
            cur_date = date_ranges[0] + datetime.timedelta(days=i)

            url = "https://prepmod.doh.wa.gov/clinic/search?q[services_name_in][]=covid&q[age_groups_name_in][" \
                  f"]=Adults&location={zip_}&search_radius={radius}+miles&q[" \
                  f"venue_search_name_or_venue_name_i_cont]=&clinic_date_eq[" \
                  f"year]={cur_date.year}&clinic_date_eq[month]={cur_date.month}&clinic_date_eq[day]={cur_date.day}&q[" \
                  f"vaccinations_name_i_cont]={vac_name}&commit=Search#search_results "
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            for div in soup.findAll("div", {"class": "md:flex-shrink"}):
                text = div.getText()
                match = re.search(r"Available Appointments:\s*(\d+)", text, re.MULTILINE)
                if match is not None:
                    appointments = int(match.group(1))
                    if appointments >= 0:
                        text = '\n\t'.join([line for line in text.split('\n') if line.strip()])
                        print(f"Found Option: {urllib.parse.quote(url)} \n\t {text} \n\n")
                        found = True

    if found:
        print("Found appointments!")
        sys.exit(1)
    else:
        print("Hard luck!")


if __name__ == "__main__":
    zip_codes = ["98005"]
    date_range = [datetime.date(2021, 4, 27), datetime.date(2021, 4, 30)]
    check_availability(zip_codes, date_range)
