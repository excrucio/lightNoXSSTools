Alat se pokre�e na na�in da mu se zada putanja do access.log datoteke, putanja do httpd.conf datoteke, 
broj toleriranih napada, trajanje pauze u minutama:

python lightNoXSSDet.py <log> <cfn> <tol> [min]

log - cijelokupan put do access.log datoteke
cfn - cijelokupan put do httpd.conf datoteke
tol - broj toleriranih napada prije nego se IP adresa s koje dolazi napad, blokira
min - trajanje pauze izme�u provjera u minutama

