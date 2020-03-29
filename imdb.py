from flask import Flask
import bs4
from bs4 import BeautifulSoup as soup
import requests
import sys
import json


app = Flask(__name__)
def scrapData(name):
    TITLE = name
    BASE_URL = 'https://www.imdb.com/find?s=tt&q='+TITLE+'&ref_=nv_sr_sm'


    page = requests.get(BASE_URL)
    parsedPage = soup(page.content,'html.parser')
    print('GOT PAGE \n')
    results = parsedPage.find(id='main')
    # print(results.prettify())

    titles_elm = results.find_all('td',class_='result_text')
    imgs_elm = results.find_all('td',class_='primary_photo')
    # print(results)

    id = 0
    jsonList = []
    img_link = []
    movies = []
    links = []

    for result in titles_elm:
        print('***************************************************************************')
        link = result.find('a')
        print('ID :',id,'  ',result.text)
        movies.append(result.text)
        links.append(link['href'])
        id = id + 1

    id = 0

    for result in imgs_elm:
        print('***************************************************************************')
        img = result.find('img')
        print('ID :',id,'  ',img['src'])
        id = id + 1
        img_link.append(img['src'])

    for i in range (0,len(movies)):
        jsonList.append({"name":movies[i],"img":img_link[i],"link":links[i][7:-1]})
    
    return json.dumps(jsonList,indent=1)


def scrapInfo(name):
    TITLE = name
    BASE_URL = 'https://www.imdb.com/title/'
    url = BASE_URL + TITLE
    page = requests.get(url)
    parsedPage = soup(page.content,'html.parser')
    print('GOT PAGE \n')
    results = parsedPage.find(id='title-overview-widget')
    summary = results.find('div',class_='summary_text')
    ratings = results.find('div',class_='ratingValue')
    # ratings = ratings.find('span')
    if(ratings!=None):
        rating = ratings.text
        jsonObj = {"plot" : summary.text,"rating":rating[:4]}
    else :
        jsonObj = {"plot" : summary.text}
    return jsonObj

def fullcast(name):
    TITLE = name
    BASE_URL = 'https://www.imdb.com/title/'+TITLE+'/fullcredits?ref_=tt_ov_wr#writers/'
    page = requests.get(BASE_URL)
    parsedPage = soup(page.content,'html.parser')
    print('GOT PAGE \n')
    results = parsedPage.find(id='fullcredits_content')
    dwTeam = results.find_all('table',class_='simpleTable simpleCreditsTable')
    posting = ['Director']
    person = []
    id = 0
    direct = dwTeam[0].find('td',class_='name')
    direct = direct.find('a')
    # print(direct.text)
    person.append(direct.text)
    id = id + 1
    dwName = dwTeam[1].find_all('td','name')
    dwPost = dwTeam[1].find_all('td','credit')
    # print(dwName)
    # print(dwPost)
    for i in range (0,len(dwName)):
        name = dwName[i].find('a')
        person.append(name.text)
        posting.append(dwPost[i].text)
    # print("POSTING :",posting)
    # print("PERSON :",person)
    fcast = results.find('table',class_='cast_list')
    fcast = fcast.find_all('tr')
    # print(fcast)
    castImage = []
    castName = []
    castRoleName = []
    for i in range (1,len(fcast)):
        rowData = fcast[i].find_all('td')
        image = rowData[0]
        # print(rowData)            
        image = image.find('a')
        image = image.find('img')
        image = image['src']
        castImage.append(image)
        actor = rowData[1]
        actor = actor.find('a')
        castName.append(actor.text)
        character = rowData[3]
        # print(rowData[3])
        character = character.find('a')
        if(character!=None):
            castRoleName.append(character.text)
        else:
            castRoleName.append("NAN")
    jsonCast =[]
    # print(castName)
    # print(castImage)
    for i in range(0,len(person)):
        jsonCast.append({"role":posting[i],"name":person[i]})
    for i in range(0,len(castName)):
        jsonCast.append({"actor":castName[i],"image":castImage[i],"roleName":castRoleName[i]})      

    return jsonCast


@app.route('/')
def index():
    jsonObj = {"message":"base URL"}
    return json.dumps(jsonObj,indent=1)

@app.route('/api/movies/<title>')
def getData(title):
    response = scrapData(title)
    return response

@app.route('/api/movies/plot/<link>')
def getPlot(link):
    plot = scrapInfo(link)
    return json.dumps(plot,indent=1)

@app.route('/api/movies/cast/<link>')
def getCast(link):
    cast = fullcast(link)
    return json.dumps(cast,indent=1)

if __name__ == '__main__':
   app.run(debug = True)