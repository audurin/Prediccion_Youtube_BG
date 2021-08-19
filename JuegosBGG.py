from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

driver = webdriver.Firefox()

name=[]
place=[]
rating1=[]
rating2=[]
voters=[]
url=[]
year=[]

link = 'https://boardgamegeek.com/browse/boardgame/page/'

for i in range(1,110):
    driver.get(f"{link}{i}")
    '''for i in range(100):
        driver.execute_script(f"window.scrollTo(0, {i*500},'smooth');")
        time.sleep(.5)
    content = driver.page_source
    soup = BeautifulSoup(content)
    canal=soup.find('yt-formatted-string', attrs={'id':'text','class':'style-scope ytd-channel-name'}).text
    suscriptores=soup.find('yt-formatted-string', attrs={'id':'subscriber-count','class':'style-scope ytd-c4-tabbed-header-renderer'}).text'''
    content = driver.page_source
    soup = BeautifulSoup(content)
    for a in soup.findAll('tr', attrs={'id':'row_'}):
        lugar=a.find('td', attrs={'class':'collection_rank'})
        liga = a.find('a', attrs={'class':'primary'})
        fecha = a.find('span', attrs={'class':'smallerfont dull'})
        cal=a.findAll('td', attrs={'class':'collection_bggrating'})
        place.append(lugar.text.replace('\t','').replace('\n',''))
        url.append(liga['href'])
        name.append(liga.text)
        if fecha is not None:
            year.append(fecha.text[1:5])
        else:
            year.append(0)
        rating1.append(cal[0].text.replace('\t','').replace('\n',''))
        rating2.append(cal[1].text.replace('\t','').replace('\n',''))
        voters.append(cal[2].text.replace('\t','').replace('\n',''))
    df = pd.DataFrame({'Lugar':place,'Juego':name,'Año':year,'Rating':rating1,'AvRating':rating2,'Calificadores':voters,'url':url}) 
    df.to_csv('JuegosBGG.csv', index=False, encoding='utf-8')
    #time.sleep(8)

driver.quit()