import os
import mechanize
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar
import pandas
import datetime

# Get the current date and time
now = datetime.datetime.now()
# Print the current date and time in a specific format
print(now.strftime("%m-%d-%Y %H:%M:%S"))

cj = CookieJar()
br = mechanize.Browser()
br.set_cookiejar(cj)
br.open("https://op.responsive.net/lt/ba727/entry.html")
br.select_form(nr=0)
br.form['id'] = os.getenv('LF_USERNAME')
br.form['password'] = os.getenv('LF_PASSWORD')
br.submit()

url_list = ["CASH", "JOBIN", "S1UTIL", "S2UTIL", "S3UTIL", "S1Q", "S2Q", "S3Q"]
url_list_4col = ["JOBT" ,"JOBREV", "JOBOUT"]
headers = ["INV"] + url_list + url_list_4col
HUMAN_HEADERS_MAP = {
    "Jobs Accepted Daily": "JOBIN",
    "Jobs Completed": "JOBOUT",
    "Daily Average Job Lead Time": "JOBT",
    "Station 1 Utilization": "S1UTIL", 
    "Station 2 Utilization": "S2UTIL",
    "Station 3 Utilization": "S3UTIL",
    "Station 1 Queue": "S1Q",
    "Station 2 Queue": "S2Q",
    "Station 3 Queue": "S3Q",
    "Cash Balance": "CASH",
    "Revenues Avg per job": "JOBREV",
    "Inventory": "INV",
}

# Replace machine headers with human readable ones
for k, v in HUMAN_HEADERS_MAP.items():
    if v in headers:
        headers[headers.index(v)] = k


LF_DATA = {}
#get INVENTORY first
inv_url = "http://op.responsive.net/Littlefield/Plot?data=INV&x=all"
soup = BeautifulSoup(br.open(inv_url), "lxml")
data = soup.find_all("script")[6].string
data = data.split("\n")[4].split("'")[3].split()
counter = 1
for i in data:
 if counter % 2 == 1:
  counter += 1
  day = float(i)
  LF_DATA[day] = []
 elif counter % 2 == 0:
  row_data = [float(i)]
  LF_DATA[day].extend(row_data)
  counter += 1

#iterate through and scrape all two-column tables
for url in url_list:
 lf_url = "http://op.responsive.net/Littlefield/Plot?data=%s&x=all" % url
 soup = BeautifulSoup(br.open(lf_url), "lxml")
 data = soup.find_all("script")[6].string
 data = data.split("\n")[4].split("'")[3].split()

 counter = 1
 for i in data:
  if counter % 2 == 0:
   day = counter/2
   LF_DATA[day].append(float(i))
   counter += 1
  else:
   counter +=1

#iterate through and scrape all four-column tables
for url in url_list_4col:
 lf_url = "http://op.responsive.net/Littlefield/Plot?data=%s&x=all" % url
 soup = BeautifulSoup(br.open(lf_url), "lxml")
 data = soup.find_all("script")[6].string
 split_data = data.split("\n")
 data0 = split_data[4].split("'")[5].split()
 
 counter = 1
 for i in data0:
  if counter % 2 == 0:
   day = counter/2
   LF_DATA[day].append(float(i))
   counter += 1
  else:
   counter +=1

# Remove fractional days
LF_DATA = {k: v for k, v in LF_DATA.items() if k.is_integer()}


df = pandas.DataFrame.from_dict(LF_DATA, orient="index")
df.columns = headers
df.sort_index(inplace=True)
df["Backlog"] = df["Jobs Accepted Daily"].cumsum() - df["Jobs Completed"].cumsum()

# Set up the Excel writer based on existence of the file
kwargs = {}
path = os.getenv('OUTPUT_FILE', 'output.xlsx')
if os.path.exists(path):
    kwargs['mode'] = 'a'
    kwargs['if_sheet_exists'] ='overlay'
else:
    kwargs['mode'] = 'w'

writer = pandas.ExcelWriter(path, **kwargs)
df.to_excel(writer, sheet_name='data')
writer._save()
print(f"Data saved to Excel file: {path}")
