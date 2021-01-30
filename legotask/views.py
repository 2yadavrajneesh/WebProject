import json

from django.http import HttpResponse
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd


# Create your views here.
def index(request):
    cic = int(request.GET.get("cic"))
    search_type = str(request.GET.get("search_type"))
    date_entry1 = request.GET.get("date_entry1")
    date_entry2 = request.GET.get("date_entry2")

    year, month, day = map(int, date_entry1.split('/'))
    year1, month1, day1 = map(int, date_entry2.split('/'))
    date1 = datetime.date(year, month, day)
    date2 = datetime.date(year1, month1, day1)
    fromdate = date1.strftime('%d/%m/%Y')
    todate = date2.strftime('%d/%m/%Y')
    page = requests.get(
        f'https://dsscic.nic.in/cause-list-report-web/registry_cause_list/1?opt=appCom&commissionname={cic}&seach_type={search_type}&search_text=&fromdate={fromdate}&todate={todate}&search_button=')
    soup = BeautifulSoup(page.content, 'html.parser')

    rows = soup.find_all('tr')

    import re

    list_rows = []
    for row in rows:
        cells = row.find_all('td')
        str_cells = str(cells)
        clean = re.compile('<.*?>')
        clean2 = (re.sub(clean, '', str_cells))
        list_rows.append(clean2)

    lst = [x.replace('\t', '').replace('\n', '').replace('">-->', '') for x in list_rows]

    df = pd.DataFrame(lst)
    df1 = df[0].str.split(',', expand=True)
    df1.head(10)
    df1[0] = df1[0].str.strip('[')
    df1 = df1.mask(df1.astype(object).eq('None')).dropna()
    df2 = df1.set_index(0, inplace=True)
    result = df2.to_json(orient="records")
    parsed = json.loads(result)

    return HttpResponse(json.dumps(parsed))
