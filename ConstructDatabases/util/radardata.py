#!/bin/python
#coding=utf-8
#
#    * File      : douban.py
#    * Author    : 
#    * Mail      : 
#    * Creation  : Mon 30 Mar 2020 04:19:46 PM CST
import numpy as np
import time
from bs4 import BeautifulSoup
import urllib.request,urllib.error
import sqlite3 
import re
import math
import pandas as pd
import os

def askUrl(url):
    header={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}
    html=""
    request=urllib.request.Request(url,headers=header)
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode("utf-8")
    except urllib.error.URLError as e :
        if(hasattr(e,"code")):
            print(e.code)
        if(hasattr(e,"reason")):
            print(e.reason)
    return html

findlink=re.compile(r'<a href="(.*?)">')
findImgsrc=re.compile(r'<img src="(.*?)"',re.S)
findTitle=re.compile(r'<span class="title">(.*)</span>')
findRate=re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findjudge=re.compile(r'<span>(\d*)人评价</span>')
findinq=re.compile(r'<span>class="inq"(.*)</span>')
findbd=re.compile(r'<p class="">(.*?)</p>',re.S)


def parserdata(html):
    soup=BeautifulSoup(html,"html.parser")
    refindimgsrc=re.compile(r'<a (.*)href="(.*?.html)"(.*)</a>',re.S)
    refindkind=re.compile(r'<p>(.*)</p>',re.S)
    datalist=[]
    for item in soup.find_all('div',class_='inc'):
        #print(str(item))
        item=str(item)
        data=[]
        srclink=re.findall(refindimgsrc,item)
        srclink=srclink[0][1]
        suburl="https://www.radartutorial.eu/19.kartei/"
        srclink=suburl+srclink
        data.append(srclink)

        kind=re.findall(refindkind,item)[0]
        kind=re.sub(r'\(.*?\)',"",kind)
        kind=kind.strip('\t')
        kind=kind.strip('\n')
        data.append(kind)

        datalist.append(data)

    datalist=[x for x in datalist if x]
    return datalist

def parserdata2(url):
    html=askUrl(url)
    soup=BeautifulSoup(html,"html.parser")

    refindimgsrc=re.compile(r'<a (.*)href="(.*?.html)"(.*)</a>',re.S)
    refindname=re.compile(r'</div>(.*)</a>',re.S)
    datalist=[]
    for item in soup.find_all('div',class_='inc'):
        item=str(item)
        data=[]

        link=re.findall(refindimgsrc,item)
        link=link[0][1]
        suburl="https://www.radartutorial.eu/19.kartei/"
        link=suburl+link
        data.append(link)

        name=re.findall(refindname,item)[0]
        name=re.sub(r'<br/>',' ',name)
        data.append(name)
        datalist.append(data)


    reslist=[[0 for i in range(len(datalist[0]))] for j in range(len(datalist))]
    for i in range(len(datalist)):
        for j in range(len(datalist[i])):
            reslist[i][j]=re.sub(r'\t','',datalist[i][j])
            reslist[i][j]=re.sub(r'\u202f','',datalist[i][j])

    return reslist

def parserdata3(url):
    datalist=[]
    try:
        data =pd.read_html(url)[0]
    except ValueError:
        return datalist

    #data=data.drop([0])
    data=data.fillna('')

    datalist=np.array(data).tolist()
    
    #for i in range(len(datalist)):
        #if 'frequency:' in datalist[i]:
            #if (len(datalist[i])==3):
                #valuelist.append(datalist[i][1]+','+datalist[i][2])
            #else:
                #valuelist.append(datalist[i][1])
    #if valuelist.count==0:
            #valuelist.append('')

    indexlist=['frequency:','pulse repetition time (PRT):','pulse repetition frequency (PRF):','pulsewidth (τ):','receive time:','dead time:','peak power:','average power:','instrumented range:','range resolution:','accuracy:','beamwidth:','hits per scan:','antenna rotation:','MTBCF:','MTTR:']
    valuelist=[]
    for x in range(len(indexlist)):
        for y in range(len(datalist)):
            if indexlist[x] in datalist[y]:
                if len(datalist[y])==3:
                    valuelist.append(datalist[y][1]+','+datalist[y][2])
                else:
                    valuelist.append(datalist[y][1])
        if valuelist.count==x:
            valuelist.append('')
    resultlist=[]
    for value in valuelist:
        result=re.sub(r'\t','',value)
        result=re.sub(r'\u202f','',result)
        resultlist.append(result)
    #data of only one radartype        
    return resultlist



def get_data(url):
    datalist=[]
    html=askUrl(url)
    #print(html)
    datalist=parserdata(html)
    print("radar types:")
    print(datalist)

    return datalist

def initdb(path):
    sql='''
    create table movie 
    (
        id integer primary key autoincrement,
        infolink text,
        prilink text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text
    )
    '''
    conn=sqlite3.connect(path)
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

def mkdir(path):
    folder=os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("-----%s new folder--------")
    else:
        print("already have a folder")


def savedata(datalist,path):
    initdb(path)
    conn=sqlite3.connect(path)
    cur=conn.cursor()
    
    for data in datalist:
        for index in range(len(data)):
            if index ==4 or index ==5:
                continue
            data[index]='"'+data[index]+'"'
        sql='''
        insert into movie(
                infolink,prilink,cname,ename,score,rated,introduction,info)
                values(%s)
            '''%",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()

def getImg(path,url,imgname):
    html=askUrl(url)
    
    findimg=re.compile(r'<a class="(.*?)" href="(.*?)" title')
    urlpre=re.sub(r'/([^/]*?)\.html','/',url)
    soup=BeautifulSoup(html,"html.parser")
    for item in soup.find_all('div',class_="pictable_c scr"):
        item=str(item)
        print(url)
        print(item)
        img=re.findall(findimg,item)
        print(img)
        try:
            img=img[0][1]
        except IndexError:
            return 

        print(img)
        imgurl=urlpre+img
        print(imgurl)
        img=re.sub(r'/','-',imgname)
        try:
            urllib.request.urlretrieve(imgurl,path+'/'+img+'.jpg')
            print("success download")
        except urllib.error.HTTPError:
            print("url error")
            return 


def main():
    url="https://www.radartutorial.eu/19.kartei/ka01.en.html"
    
    #download page
    datalist=get_data(url)
    #for data in datalist:
    #    mkdir(data[1])
    res=[]
    for i in datalist:
        temp=parserdata2(i[0]) 
        for t in temp:
            radarinfo=parserdata3(t[0])
            if len(radarinfo)==0:
                continue
            f=open('./info.txt','a+')
            radarinfo=map(lambda x: x+'\t',radarinfo);
            f.write(t[1]+'\t')
            f.writelines(radarinfo)
            f.write('\n')
            f.close()
            time.sleep(1)


        print(temp)
        res.append(temp)
    #print(res)
    print(len(res))
    print(len(res[0]))
    print(len(res[0][0]))

       
    #for i in range(len(res)):

    #save data
    dbpath="movie.db"
    #savedata(datalist,dbpath)


if __name__=="__main__":
    main()

    
    pass

