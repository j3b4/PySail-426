# -*- coding: utf-8 -*-
#Copyright (C) 2012 Riccardo Apolloni
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For detail about GNU see <http://www.gnu.org/licenses/>.
'''
import math

#COSTANTI
RaggioTerrestre=60.0*360/(2*math.pi)#nm
#FUNZIONI
def puntodistanterotta(latA,lonA,Distanza,Rotta):
    #non funziona in prossimita' dei poli
    #dove può risultare latC>90, log(tan(latC/...))=log(<0)   (*)
    a=Distanza*1.0/RaggioTerrestre
    latB=latA+a*math.cos(Rotta)
    if math.copysign(latA-latB,1)<=math.radians(0.1/3600.0):
        q=math.cos(latA)
    else:
        Df=math.log(math.tan(latB/2+math.pi/4)/math.tan(latA/2+math.pi/4),math.e)#(*)
        q=(latB-latA)/Df
    lonB=lonA-a*math.sin(Rotta)/q
    return latB,lonB
def lossodromica(latA,lonA,latB,lonB):
    #non funziona in prossimita' dei poli
    #per latB=-90: math domain error log(0)
    #per latA=-90 [zero divison error]
    #per A==B ritorna (0.0,0.0)
    #if latA==latB:
    if  math.copysign(latA-latB,1)<=math.radians(0.1/3600.0):
        q=math.cos(latA)
    else:
        Df=math.log(math.tan(latB/2+math.pi/4)/math.tan(latA/2+math.pi/4),math.e)
        q=(latB-latA)*1.0/Df
    Distanza=RaggioTerrestre*((latA-latB)**2+(q*(lonA-lonB))**2)**0.5
    Rotta=math.atan2(-q*(lonB-lonA),(latB-latA))
    if Rotta<0:Rotta=Rotta+2.0*math.pi#atan2:[-pi,pi]
    return Distanza,Rotta
def ortodromica(latA,lonA,latB,lonB):
    Distanza=math.cos(latA)*math.cos(latB)*math.cos(lonB-lonA)+math.sin(latA)*math.sin(latB)
    Distanza=RaggioTerrestre*math.acos(Distanza)
    x=math.cos(latA)*math.sin(latB)-math.sin(latA)*math.cos(latB)*math.cos(lonB-lonA)
    y=math.sin(lonB-lonA)*math.cos(latB)
    Rotta=math.atan2(-y,x)
    if Rotta<0:Rotta=Rotta+2.0*math.pi#atan2:[-pi,pi]
    return Distanza,Rotta
def riduci360(alfa):
    n=int(alfa*0.5/math.pi)
    n=math.copysign(n,1)
    if alfa>2.0*math.pi:
        alfa=alfa-n*2.0*math.pi
    if alfa<0:
        alfa=(n+1)*2.0*math.pi+alfa
    if alfa>2.0*math.pi or alfa<0:
        print "errore riduci360"
    return alfa
def riduci180(alfa):
    if alfa>math.pi:
        alfa=alfa-2*math.pi
    if alfa<-math.pi:
        alfa=2*math.pi+alfa
    if alfa>math.pi or alfa<-math.pi:
        print "errore riduci180"
    return alfa
def scartorotta(rotta1,rotta2):
    #rende l'angolo [0-math.pi] tra rotta1 e rotta2
    scarto=math.copysign(rotta1-rotta2,1)
    if scarto>math.pi:
        scarto=2*math.pi-scarto
    return scarto
def stampalat(lat):
    #ritorna una stringa di testo in formato xxGradi,xxPrimi, N/S
    latdecimali=math.copysign(math.degrees(lat),1)
    latgradi=int(latdecimali)
    latprimi=(latdecimali-latgradi)*60
    if latprimi>59.51:
        latgradi=latgradi+1
        latprimi=0
    else:
        if latprimi-int(latprimi)>0.51:
            latprimi=int(latprimi)+1
        else:
            latprimi=int(latprimi)
    if lat>0:segno="N"
    else: segno="S"
    gradi="%2d"%latgradi
    primi="%2d"%latprimi
    lat=gradi.replace(" ","0")+u"°"+primi.replace(" ","0")+"'"+segno
    return lat
def stampalon(lon):
    londecimali=math.copysign(math.degrees(lon),1)
    longradi=int(londecimali)
    lonprimi=(londecimali-longradi)*60
    if lonprimi>59.51:
        longradi=longradi+1
        lonprimi=0
    else:
        if lonprimi-int(lonprimi)>0.51:
            lonprimi=int(lonprimi)+1
        else:
            lonprimi=int(lonprimi)
    if lon>0:segno="W"
    else: segno="E"
    gradi="%3d"%longradi
    primi="%2d"%lonprimi
    lon=gradi.replace(" ","0")+u"°"+primi.replace(" ","0")+"'"+segno
    return lon
