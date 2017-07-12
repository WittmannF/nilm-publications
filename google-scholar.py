import requests
from bs4 import BeautifulSoup
import pandas as pd

use_proxy = False
proxy = '212.237.36.234:3128'
start = 440
f_name = 'data_start_{}.csv'.format(start)

# Main methods
def get_citations(content):
    out = 0
    for char in range(0,len(content)):
        if content[char:char+9] == 'Cited by ':
            init = char+9                          
            for end in range(init+1,init+6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)
    
def get_year(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[char-5:char-1]
    try:
        if not out.isdigit():
            out = 0
    except:
        out = 0
        print('theres an error with year in the content {}'.format(content))
    return int(out)

def get_author(content):
    out = 'NA'
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[2:char-1]
            break
    return out

def extract_features(mydivs):
    
    links = list()
    title = list()
    citations = list()
    year = list()
    rank = list()
    author = list()

    for div in mydivs:
        try:
            links.append(div.find('h3').find('a').get('href'))
        except: # catch *all* exceptions
            links.append('Look manually at: https://scholar.google.com/scholar?start='+str(n)+'&q=non+intrusive+load+monitoring')

        try:
            title.append(div.find('h3').find('a').text)
        except: 
            title.append('Could not catch title')

        citations.append(get_citations(str(div.format_string)))
        year.append(get_year(div.find('div',{'class' : 'gs_a'}).text))
        author.append(get_author(div.find('div',{'class' : 'gs_a'}).text))
        
    data = pd.DataFrame(zip(author, title, citations, year, links), 
                        columns=['Author', 'Title', 'Citations', 'Year', 'Source'])
    
    return data

n_results = 1320
data = pd.DataFrame()

proxies = {
  'http': 'http://{}'.format(proxy),
  'https': 'http://{}'.format(proxy)
}


session = requests.Session()

for n in range(start, n_results, 10):
    url = "https://scholar.google.com.br/scholar?start={}&hl=en&as_sdt=0,5&sciodt=0,5&cites=13659967341396885001&scipsc=".format(n)
    page = session.get(url, proxies=proxies) if use_proxy else session.get(url)
    c = page.content
    
    if 'not a robot' in c:
        print("Robot Check at n = {}!".format(n))
        break

    # Create parser
    soup = BeautifulSoup(c, 'html.parser')

    # Get stuff
    mydivs = soup.findAll("div", { "class" : "gs_r" })
    
    d = extract_features(mydivs)
    
    data = data.append(d)

print('Done! Saving to CSV')

data.to_csv(f_name, encoding='utf-8')
