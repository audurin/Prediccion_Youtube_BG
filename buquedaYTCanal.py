from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from langdetect import detect
import pandas as pd

num=[]
urlChannel=[]
suscribers=[]
channelViews=[]
channelDate=[]
channelIdiom=[]

colnames=['numero','canal','apariciones'] 
data = pd.read_csv("canalesfaltantes.csv", names=colnames, header=None) 
driver = webdriver.Firefox()

def createLink(palabra):
    link = "https://www.youtube.com"
    link = f"{link}{palabra}/about"
    return link

for index, row in data.iterrows():
    palabra = row['canal']
    link = createLink(palabra)
    driver.get(f"{link}")
    content = driver.page_source
    soup = BeautifulSoup(content)
    suscriptores=soup.find('yt-formatted-string', attrs={'id':'subscriber-count'})
    der = soup.find('div', attrs={'id':'right-column'})
    izq = soup.find('div', attrs={'id':'left-column'})
    #busqueda de views y fecha
    d=der.findAll('yt-formatted-string')
    d2=d[1].findAll('span',attrs={'class':'style-scope yt-formatted-string'})
    #busqueda idioma
    descripcion=izq.find('yt-formatted-string', attrs={'id':'description'})
    try:
        idioma = detect(descripcion.text)
    except:
        idioma = "error"
    


    num.append(row['numero'])
    urlChannel.append(row['canal'])
    suscribers.append(suscriptores.text.replace(' subscribers',''))
    channelDate.append(d2[1].text)
    channelViews.append(d[2].text.replace(' views','').replace(',',''))
    channelIdiom.append(idioma)
    df = pd.DataFrame({'Numero':num,'URL':urlChannel,'Suscriptores':suscribers,'Fecha':channelDate,'views':channelViews,'idioma':channelIdiom}) 
    df.to_csv('dataCannelsfaltantes.csv', index=False, encoding='utf-8')
       
driver.quit()