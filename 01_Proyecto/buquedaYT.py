from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from langdetect import detect


game=[]
urlGame=[]
videoName=[]
words=[]
place=[]
rating1=[]
rating2=[]
voters=[]
year=[]
views=[]
videoDays=[]
videoURL=[]
channelName=[]
channelURL=[]
idiom=[]
coincidencias=[]
colnames=['lugar','juego','palabras','ano','rating','avrating','voters','url'] 
data = pd.read_csv("juegosbase.csv", names=colnames, header=None) 
driver = webdriver.Firefox()

def scroll_down_page(driver, speed=8):
    current_scroll_position, new_height= 0, 1
    while current_scroll_position <= new_height:
        current_scroll_position += speed
        driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
def createLink(palabras):
    link = "https://www.youtube.com/results?search_query=board+game"
    for i in range(len(palabras)):
        link = f"{link}+{palabras[i]}"
    link = f"{link}&sp=CAMSAhAB"
    return link
def asignaDias(fecha):
    if fecha =='No views':
        return 1
    elif fecha.find('minute')!=-1:
        return 1
    elif fecha.find('hour')!=-1:
        return 1
    elif fecha.find('day')!=-1:
        if fecha.find('Streamed')!=-1:
            fin = fecha.find(' ',9)
            return int(fecha[9:fin].replace(',',''))
        else:
            fin = fecha.find(' ')
            return int(fecha[0:fin].replace(',',''))
    elif fecha.find('week')!=-1:
        if fecha.find('Streamed')!=-1:
            fin = fecha.find(' ',9)
            return int(fecha[9:fin].replace(',',''))*7
        else:
            fin = fecha.find(' ')
            return int(fecha[0:fin].replace(',',''))*7
    elif fecha.find('month')!=-1:
        if fecha.find('Streamed')!=-1:
            fin = fecha.find(' ',9)
            return int(fecha[9:fin].replace(',',''))*30
        else:
            fin = fecha.find(' ')
            return int(fecha[0:fin].replace(',',''))*30
    elif fecha.find('year')!=-1:
        if fecha.find('Streamed')!=-1:
            fin = fecha.find(' ',9)
            return int(fecha[9:fin].replace(',',''))*365
        else:
            fin = fecha.find(' ')
            return int(fecha[0:fin].replace(',',''))*365
    else:
        return 0

def coincidencia(nombre,palabras):
    numero=0
    for palabra in palabras:
        if nombre.find(palabra)!=-1:
            numero+=1
    return (numero/len(palabras))

    

for index, row in data.iterrows():
    juego=row['juego'].lower()
    juego = juego.replace(':','').replace('&','')
    palabras = juego.split()
    link = createLink(palabras)
    driver.get(f"{link}")
    scroll_down_page(driver)
    content = driver.page_source
    soup = BeautifulSoup(content)
    for a in soup.findAll('ytd-video-renderer', attrs={'class':'style-scope ytd-item-section-renderer'}):
        nombre=a.find('a', attrs={'id':'video-title'})
        general=nombre['aria-label']
        print(general)
        fin = general.rfind(' ')
        inicio = general.rfind(' ',0,fin)
        if general[inicio+1:fin].replace(',','')=='No':
            vistas=0
        else:
            vistas=int(general[inicio+1:fin].replace(',',''))
        meses = a.findAll('span', attrs={'class':'style-scope ytd-video-meta-block'})
        canal = a.find('a', attrs={'class':'yt-simple-endpoint style-scope yt-formatted-string'})
        inicio2 = general.find(f"by {canal.text}")+len(f"by {canal.text}")+1
        dias = general[inicio2:inicio]
        
        #des = a.find('yt-formatted-string', attrs={'class':'metadata-snippet-text style-scope ytd-video-renderer'})
        #print(f"{type(des)} - {nombre['title']}")
        #if des is not None:
        #    descripcion = des.findAll('span', attrs={'class':'style-scope yt-formatted-string'})
        #else:
        #    descripcion = 0
        
        game.append(row['juego'])
        urlGame.append(row['url'])
        videoName.append(nombre['title'])
        words.append(row['palabras'])
        place.append(int(row['lugar']))
        rating1.append(row['rating'])
        rating2.append(row['avrating'])
        voters.append(int(row['voters']))
        year.append(int(row['ano']))
        views.append(vistas)
        videoURL.append(nombre['href'])
        videoDays.append(dias)
        coincidencias.append(coincidencia(nombre['title'].lower(),palabras))
        channelName.append(canal.text)
        channelURL.append(canal['href'])
        #if isinstance(descripcion, list) and len(descripcion)>0:
        #    idiom.append(detect(descripcion[0].text))
        #else:
        #    idiom.append('en')
    df = pd.DataFrame({'Juego':game,'JuegoURL':urlGame,'nombreVideo':videoName,'Palabras':words,'Lugar':place,'rating':rating1,'avRating':rating2,'Voters':voters,'Ano':year,'Vistas':views,'URLVideo':videoURL,'Desde':videoDays,'coincidencias':coincidencias,'canal':channelName,'canalURL':channelURL}) 
    df.to_csv('dataVideos.csv', index=False, encoding='utf-8')

driver.quit()