from urllib.request import urlopen
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re

SOUNDINGS_PAGE_URL = 'http://weather.uwyo.edu/cgi-bin/sounding'
STATION_NUMBER_BUDAPEST = 12843

def obtainWeatherDataList(date):
    data = {}
    data['region'] = 'europe'
    data['TYPE'] = 'TEXT:LIST'
    data['YEAR'] = date.year
    data['MONTH'] = date.month
    data['FROM'] = str(date.day) + ('00' if date.hour < 12 else '12')
    data['STNM'] = STATION_NUMBER_BUDAPEST
    page = urlopen(SOUNDINGS_PAGE_URL + '?' + urlencode(data))
    soup = BeautifulSoup(page.read(), 'html.parser')
    return soup.find('pre').get_text()

#  PRES   HGHT   TEMP   DWPT   RELH   MIXR   DRCT   SKNT   THTA   THTE   THTV
WEATHER_DATA_LIST_FMT = \
    '\\s*(?P<pres>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<hght>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<temp>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<dwpt>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<relh>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<mixr>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<drct>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<sknt>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<thta>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<thte>[+-]?[0-9]+(?:\\.[0-9]+)?)' +\
    '\\s+(?P<thtv>[+-]?[0-9]+(?:\\.[0-9]+)?)'

def parseWeatherDataList(the_list):
    data = []
    for line in the_list.split('\n'):
        match = re.search(WEATHER_DATA_LIST_FMT, line)
        if (match is not None):
            data.append({
                'hght': float(match.group('hght')),
                'pres': float(match.group('pres')),
                'temp': float(match.group('temp')),
                'wdir': float(match.group('drct')),
                'wspd':(float(match.group('sknt')) * 0.514444444444)
            })
    return data

def getWeatherData(date):
    list = obtainWeatherDataList(date)
    return parseWeatherDataList(list)