#ova skripta gleda apache log datoteke (default je access_log) i traži sumnjive 

import json
import re
import sys
import time
import os.path
import shutil
import platform

filter_file="filteri.json"
log_file=''
httpd_file=''
blokirani_file='blokirani.txt'
pauza=5
tolerate=5

def provjeri(ip):
    if os.path.isfile(blokirani_file):
        blok=open(blokirani_file,'r').readlines()
        for i in blok:
            if ip==i.rstrip():
                return False
    return True

def cisti(ip):
    if os.path.isfile('cudni.txt'):
        cudni0=open('cudni.txt','r').readlines()
        cudni=open('cudni.txt','w')
        for lin in cudni0:
            lin=lin.rstrip()
            if (lin!=ip):
                cudni.write(ip+"\n")
        cudni.close()

def blokiraj(ip):
    cisti(ip)
    shutil.copyfile(httpd_file,httpd_file+".old")
    ima=0

    blok=open(blokirani_file,"a")
    blok.write(ip+"\n")
    blok.close()
    httpd=open(httpd_file,'r').readlines()
    tmp=open('temp.txt','w')
    for lin in httpd:
        if re.search("</Directory>",lin) and ima==1:
            break
        if re.search("<Directory />#start blokade",lin) and ima!=1:
            ima=1
        tmp.write(lin)
    if ima==0:
        tmp.write("<Directory />#start blokade\n")
    tmp.write("Deny from "+ip+"\n")
    tmp.write("</Directory>")
    tmp.close()
    os.remove(httpd_file)
    shutil.copyfile("temp.txt",httpd_file)
    os.remove("temp.txt")

    
def server_restart():
    print("Molimo ponovno pokrenite Apache poslužitelj da promjene stupe na snagu")

    
def upute():    
    print("Alat se koristi tako da mu se zada putanja do access.log datoteke, putanja do httpd.conf datoteke,")
    print("broj toleriranih napada, trajanje pauze u minutama:\n")
    print("python lightNoXSSDet.py <log> <cfn> <tol> [min] \n")
    print("   log - cijelokupan put do access.log datoteke")
    print("   cfn - cijelokupan put do httpd.conf datoteke")
    print("   tol - broj toleriranih napada prije nego se IP adresa s koje dolazi napad, blokira")
    print("   min - trajanje pauze između provjera u minutama")
    print("\n")
    print("Ovaj alat analizira log datoteke (dnevnike) koje zapisuje Apache Server.")
    print("Točnije, analizira access.log datoteku na taj način da gleda ima li kakvih napada unutar")
    print("zapisanih zahtjeva te, ako je broj napada sa iste IP adrese prešao broj koji je korisnik definirao,")
    print("blokira daljnji pristup s te IP adrese. Blokirane ip adrese se zapisuju u datoteku blokirani.txt")
    print("na istom mjestu gdje je i alat.")
    print("")
    print("Može služiti i za provjeru ostalih log datoteka, ako su u Common Log formatu.")
    print("http://en.wikipedia.org/wiki/Common_Log_Format")
    print("")
    print("Za svaki detektirani napad zapisuje, unutar datoteke cudni.log, u novi red IP adresu")
    print("s koje je pristigao napad")
    print("")
    print("Datoteka cudni.log se nalazi na istome mjestu kao i alat.")
    print("Traženje napada se aktivira svakih 5 minuta, ako drugačije nije zadano.")
    print("Ako se konzolni prozor zatvori, skripta prestaje s radom.\n")
    exit(1)
    

if len(sys.argv)<3:
    upute()

if not os.path.isfile(sys.argv[1]):
    upute()
    
if not os.path.isfile(sys.argv[2]):
    upute()
    
if not re.match("[0-9]+",sys.argv[3]):
    upute()

if len(sys.argv)>=3 and not re.match("[0-9]+",sys.argv[4]):
    upute()
else:
    pauza=float(sys.argv[4])
    
log_file=sys.argv[1]
httpd_file=sys.argv[2]
tolerate=int(round(float(sys.argv[3])))
    
def cls():
    os.system(['clear','cls'][os.name == 'nt'])
    
cls()

print(log_file)
print(httpd_file)
print(tolerate)
print(pauza)
while True:
    #učitaj filtere
    #do svakog pravila se pristupa kao: filteri['filters']['filter'][<ID>]['rule']
    #gdje je <ID> redni broj pravila počevši od 0
    filteri=json.load(open(filter_file))

    log=open(log_file,'r')

    opasan={}
    stari= {}

    if os.path.isfile('cudni.txt'):
        cudni=open('cudni.txt','r')
        for lin in cudni:
            lin=lin.rstrip('\n')
            if lin in stari:
                stari[lin]+=1
            else:
                stari[lin]=1
        cudni.close()

        opasan=stari
    ip_cudni=open('cudni.txt','w')
    for line in log:
        #razbijemo zapis u logu da kasnijem možemo spremiti IP adresu, ako je potrebno
        #                      1          2      3       4          5       6                          7       8          9       0
        zapis=re.compile(r'^([0-9.:]+).+-(.*)\[(.+)[-|+](\d+)\] "([A-Z]+)?(.+) (HTTP|HTTPS)/\d.\d" (\d+)(\s[\d]+)?(\s"(.+)" )?(.*)$').match(line.rstrip('\n'))

        for reg in filteri['filters']['filter']:
            if re.compile(reg['rule']).search(zapis.group(6))!=None:
                #u slučaju da je sumnjiv zahtjev, zapisati IP adresu
                ip_cudni.write(zapis.group(1)+'\n')
                if zapis.group(1) in opasan:
                    opasan[zapis.group(1)]+=1
                else:
                    opasan[zapis.group(1)]=1
                break
        
    log.close();
    ip_cudni.close();

    #provjera koliko se puta ponovilo da je netko napao
    #ako je više od tolerate puta, prijavi i blokiraj
    for ip in opasan:
        if opasan[ip]>tolerate:
            if provjeri(ip):
                print('\nOva IP adresa je napala više od '+str(tolerate)+' puta: ')
                print(ip,' - ',opasan[ip])
                blokiraj(ip)
                print('I sada je u potpunosti blokirana unutar httpd.conf.')
                server_restart()
                print('')
        else:
            print(".",end="")
            
    #pauziraj        
    time.sleep(pauza*60)
    
    