# -*- coding: utf-8 -*-
# Copyright (C) 2012 Riccardo Apolloni
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
from Navigation import *

# CONSTANTS
MIOWP = (math.radians(44), math.radians(10))  # (lat,lon) N>0, E>0
# I think it is a waypoint  only used during testing (see below)


# OBJECTS
class Elipsis:  # Ellissi
    '''
    Elipsis Class might only be used in isochrones.
    '''
    # X, Y coordinates Vs. absolute reference, Y at the top
    # coordinates x and y vs. Reference related (x on the major ellipse)
    # Alfa for angles to the north,
    # alfa for angles to the major axis of the ellipse

    def __init__(self,
                 major_axis=100,    # assemaggiore/major_axis
                 eccentricity=1.5,  # eccentr/eccentricity
                 directrix=0.0):    # direttrice/directrix
        # directrix: "compass" degrees of semi-major axis
        self.a = float(major_axis)
        self.e = float(eccentricity)
        self.d = directrix

    def draw(self):  # disegna/draw
        pti = []
        for t in range(0, 361):  # eq. parametrica
            t = math.radians(t)
            x = self.a * math.cos(t)
            b = self.a / self.e
            y = b * math.sin(t)
            X = x * math.sin(self.d) - y * math.cos(self.d)
            Y = x * math.cos(self.d) + y * math.sin(self.d)
            pti.append((X, Y))
        return pti

    def calcolaparametri(self, X, Y):
        # calcola l'ellise passante per XY, variando il semiasse maggiore
        x = X * math.sin(self.d) + Y * math.cos(self.d)
        y = -X * math.cos(self.d) + Y * math.sin(self.d)
        r = (x**2 + y**2)**0.5
        teta = math.atan2(y, x)
        a = self.a
        b = a / self.e
        r1 = a * b / ((b * math.cos(teta))**2 +
                      (a * math.sin(teta))**2)**0.5  # eq. polare
        n = 0
        while (r - r1)**2 > 0.0001 and n < 10**6:
            n = n + 1
            a = a + (r - r1)
            b = a / self.e
            r1 = a * b / ((b * math.cos(teta))**2 +
                          (a * math.sin(teta))**2)**0.5
        self.a = a

    def calcolatangente(self, Teta):
        # rende la (direzione M della) tangente all'ellisse
        # nel punto (dell'ellisse rilevato per ) Teta
        # (in gradi bussola, dal centro dell'ellisse)
        teta = self.d - Teta
        t = math.atan2(self.e * math.sin(teta), math.cos(teta)
                       )  # relazione tra parametro t e Teta
        x = self.a * math.cos(t)
        y = self.a / self.e * math.sin(t)
        a = self.a
        b = self.a / self.e
        m = -math.atan2(b**2 * x, a**2 * y)
        M = self.d - m
        return M

    def raggiocurvatura(self, Teta):
        # rende il raggio di curvatura dell'ellisse
        # nel punto (dell'ellisse rilevato per ) Teta (in gradi bussola,
        # dal centro dell'ellisse)
        teta = self.d - Teta
        t = math.atan2(self.e * math.sin(teta), math.cos(teta)
                       )  # relazione tra parametro t e Teta
        a = self.a
        b = self.a / self.e
        curv = a * b / ((a * math.sin(t))**2 + (b * math.cos(t))**2)**(1.5)
        return 1.0 / curv


class Bezier:
    def __init__(self, control_points=[]):  # pticontrollo/control_points
        self.control_points = control_points
        '''
        JB: I think this  class is crucial to the interpolation of the
        boat polars.  But I'll learn more.

        Or it might be for nothing more than drawing an image of the boat.
        '''
        # list of control points for the curve

    def calcolavalore(self, t):
        # makes a point in the Bezier curve.
        # not translated yet.
        n = len(self.control_points) - 1
        x = 0
        y = 0
        for k in range(0, n + 1):
            weight = ((1 - t)**(n - k)) * (t**k) * cfbinomiale(n, k)
            # peso/weight
            x = x + self.control_points[k][0] * weight
            y = y + self.control_points[k][1] * weight
        return (x, y)


class Polar:  # Polare/Polar
    '''
    Polar data (file.pol), ranked by TWA (rows), TWS (columns)
    '''

    def __init__(self, polar_file=""):  # filepolare/polar_file
        # read the Polar Table in
        self.TWS = []  # array of TWS (wind speed values)
        self.TWA = []  # array TWA (wind angle) [0,180]
        self.vmgdict = {}
        self.SpeedTable = []
        File = open(polar_file, "r")
        line = File.readline()
        tws = line.split()
        for i in range(1, len(tws)):
            self.TWS.append(float(tws[i]))
        line = File.readline()
        while line != "":
            dato = line.split()
            twa = float(dato[0])
            self.TWA.append(math.radians(twa))
            '''Interesting even in the polar object twa stored as a radian'''
            speedline = []
            for i in range(1, len(dato)):
                speed = float(dato[i])
                speedline.append(speed)
            self.SpeedTable.append(speedline)
            line = File.readline()
        File.close()

    def Speed(self, TWS, TWA):
        '''
        This function applies the polar to the current wind speed
        and angle and returns the resulting boat speed.
        The input TWS and TWA are single values?
        '''
        if TWA == 0:
            return 0.0
        'boat is in irons, no need to look anything up.'
        # Next TWS might be between two charted points
        tws1 = 0
        tws2 = 0
        for k in range(0, len(self.TWS)):
            if TWS >= self.TWS[k]:
                tws1 = k
        for k in range(len(self.TWS) - 1, 0, -1):
            # range (start, stop, step)
            '''
            So we start with the lenght of the TWS array minus 1,
            step down until we reach 0. (first entry in the list)
            And if we reach a value that is less or eq. to the input
            then we'll store in in tws 2.  This gives us our top bound
            .  We now know that TWS is between tws1 and tws2
            '''
            if TWS <= self.TWS[k]:
                tws2 = k
        if tws1 > tws2:  # in case input TWS is off the chart
            tws2 = len(self.TWS) - 1
            '''
            So this surprises me how is the length of the array the speed
            value?
            '''
        twa1 = 0
        twa2 = 0
        for k in range(0, len(self.TWA)):
            if TWA >= self.TWA[k]:
                twa1 = k
        for k in range(len(self.TWA) - 1, 0, -1):
            if TWA <= self.TWA[k]:
                twa2 = k
            '''
            Same as with TWS
            '''
        speed1 = self.SpeedTable[twa1][tws1]
        speed2 = self.SpeedTable[twa2][tws1]
        speed3 = self.SpeedTable[twa1][tws2]
        speed4 = self.SpeedTable[twa2][tws2]
        '''
        Now this is interesting, these four values.
        S1  = the bottom angle and speed,
        S4 = the top and 2&3 are in between.
        '''
        if twa1 != twa2:
            '''
            I think this means that TWA was not an exact match therefore we
            have to interpolate.
            '''
            speed12 = speed1 + (speed2 - speed1) * (TWA - self.TWA[twa1]) / (
                self.TWA[twa2] - self.TWA[twa1])  # interpolation of TWA
            speed34 = speed3 + (speed4 - speed3) * (TWA - self.TWA[twa1]) / (
                self.TWA[twa2] - self.TWA[twa1])  # interpolation of TWA
        else:
            '''
            But if TWA was an exact hit on the polar then... this simplifies
            interpolation a little.
            '''
            speed12 = speed1
            speed34 = speed3
        if tws1 != tws2:
            '''
            Then we do the same for the speed and get our result.
            This is really cool. I hope I can understand it later and reproduce
            it.
            '''
            speed = speed12 + (speed34 - speed12) * (TWS - self.TWS[tws1]) / (
                self.TWS[tws2] - self.TWS[tws1])
        else:
            speed = speed12
        return speed * 0.90  # arbitrarily degrade performance

    def Reaching(self, TWS):
        '''
        I kinda see what this does but fail to understand why
        I guess it picks out the highest speed tack for a given
        wind speed. Important I guess for optimization.
        '''
        maxspeed = 0
        TWAmaxspeed = 0
        for twa in range(0, 181):
            TWA = math.radians(twa)
            speed = self.Speed(TWS, TWA)
            if speed > maxspeed:
                maxspeed = speed
                TWAmaxspeed = TWA
        return (maxspeed, TWAmaxspeed)

    def maxVMGtwa(self, tws, twa):
        if not self.vmgdict.has_key((tws, twa)):
            twamin = max(0, twa - math.pi / 2)
            twamax = min(math.pi, twa + math.pi / 2)
            alfa = twamin
            maxvmg = -1.0
            while alfa < twamax:
                v = self.Speed(tws, alfa)
                vmg = v * math.cos(alfa - twa)
                '''
                Okay. This is like looking at a polar to see VMG upwind.
                '''
                if vmg - maxvmg > 10**-3:  # 10**-3 errore tollerato
                    maxvmg = vmg
                    twamaxvmg = alfa
                alfa = alfa + math.radians(1)
            self.vmgdict[tws, twa] = (maxvmg, twamaxvmg)
        return self.vmgdict.get((tws, twa))

    def maxVMGup(self, TWS):
        vmguptupla = self.maxVMGtwa(TWS, 0)
        return (vmguptupla[0], vmguptupla[1])

    def maxVMGdown(self, TWS):
        vmgdowntupla = self.maxVMGtwa(TWS, math.pi)
        return (-vmgdowntupla[0], vmgdowntupla[1])

    def SpeedRoutage(self, TWS, TWA):
        UP = self.maxVMGup(TWS)
        vmgup = UP[0]
        twaup = UP[1]
        DOWN = self.maxVMGdown(TWS)
        vmgdown = DOWN[0]
        twadown = DOWN[1]
        v = 0.0
        if TWA >= twaup and TWA <= twadown:
            v = self.Speed(TWS, TWA)
        else:
            if TWA < twaup:
                v = vmgup / math.cos(TWA)
            if TWA > twadown:
                v = vmgdown / math.cos(TWA)
        return v

    def TWAroutage(self, TWS, TWA):
        UP = self.maxVMGup(TWS)
        vmgup = UP[0]
        twaup = UP[1]
        DOWN = self.maxVMGdown(TWS)
        vmgdown = DOWN[0]
        twadown = DOWN[1]
        if TWA >= twaup and TWA <= twadown:
            twa = TWA
        else:
            if TWA < twaup:
                twa = twaup
            if TWA > twadown:
                twa = twadown
        return twa
'''
I'm probably not easily going to understand the code by simply reading and even
translating the variables and comments.  Instead I have to try implementing my
own library ... I'll learn on a need to know basis I suppose.
'''

class Barca:
    def __init__(self,
                 pos=(0.0, 0.0),
                 log=0.0,
                 twa=0.0,
                 tw=(0.0, 0.0),
                 polar_file=""):
        self.Pos = pos  # tupla (lat,lon) in radianti
        self.Log = log
        self.TWA = twa  # positivo per mure a dritta, [-180,180]
        self.TW = tw  # tupla (TWD,TWS) TWD in radianti, TWS in knts
        self.Plr = Polar(polar_file)
        bezier = Bezier([(-40.0, -75.0), (-60.5, 55.0),
                         (0.0, 125.0)])  # icona barca
        icona = [(0.0, -75.0)]
        for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            icona.append(bezier.calcolavalore(i))
        iconasimmetrica = []
        for i in range(1, len(icona)):
            iconasimmetrica.append((-icona[i][0], icona[i][1]))
        iconasimmetrica.reverse()
        self.Icona = icona + iconasimmetrica + [(0.0, -75.0)]

    '''
    def Orza(self):
        #Orza di 1 grado
        if self.TWA-math.radians(1)>0.0 and self.TWA<=math.pi:#mure a dx
            self.TWA=self.TWA-math.radians(1)
        if self.TWA+math.radians(1)<0.0 and self.TWA>=-math.pi:#mure a sx
            self.TWA=self.TWA+math.radians(1)
    def Puggia(self):
        #Puggia di 1 grado
        if self.TWA>=0 and self.TWA<math.pi:#mure a dx
            self.TWA=self.TWA+math.radians(1)
            if self.TWA>math.pi:self.TWA=math.pi
        if self.TWA<=0 and self.TWA>-math.pi:#mure a sx
            self.TWA=self.TWA-math.radians(1)
            if self.TWA<-math.pi:self.TWA=-math.pi
    '''

    def Orza(self):  # revisione 29/11/2013
        twa = math.copysign(self.TWA, 1)
        twa = twa - math.radians(1)
        if twa < 0:
            twa = 0
        self.TWA = math.copysign(twa, self.TWA)

    def Puggia(self):
        twa = math.copysign(self.TWA, 1)
        twa = twa + math.radians(1)
        if twa > math.pi:
            twa = math.pi
        self.TWA = math.copysign(twa, self.TWA)

    def CambiaMura(self):
        self.TWA = -self.TWA

    def Muovi(self, dt):
        v = self.Speed()
        pos = puntodistanterotta(self.Pos[0], self.Pos[1], v * dt, self.HDG())
        self.Pos = pos
        self.Log = self.Log + v * dt

    def MuoviRoutage(self, dt):
        v = self.SpeedRoutage()
        pos = puntodistanterotta(self.Pos[0], self.Pos[1], v * dt, self.HDG())
        self.Pos = pos
        self.Log = self.Log + v * dt

    def Speed(self):
        twa = math.copysign(self.TWA, 1)
        return self.Plr.Speed(self.TW[1], twa)

    def SpeedRoutage(self):
        twa = math.copysign(self.TWA, 1)
        return self.Plr.SpeedRoutage(self.TW[1], twa)

    def HDG(self):
        return riduci360(self.TW[0] - self.TWA)  # TWA positivo mure a dritta

    def BRG(self, wp):
        losso = lossodromica(self.Pos[0], self.Pos[1], wp[0], wp[1])
        return losso[1]

    def BRGGPS(self, wp):
        orto = ortodromica(self.Pos[0], self.Pos[1], wp[0], wp[1])
        return orto[1]

    def Dist(self, wp):
        losso = lossodromica(self.Pos[0], self.Pos[1], wp[0], wp[1])
        return losso[0]

    def CMG(self, rlv):
        scarto = scartorotta(self.HDG(), rlv)
        return self.Speed() * math.cos(scarto)

    def VMGWP(self, wp):
        losso = lossodromica(self.Pos[0], self.Pos[1], wp[0], wp[1])
        scarto = scartorotta(self.HDG(), losso[1])
        return self.Speed() * math.cos(scarto)

    def TWAmaxVMGWP(self, wp):
        rlv = self.BRG(wp)
        return self.TWAmaxCMG(rlv)

    def TWAmaxCMG(self, rlv):
        twabrg = riduci180(self.TW[0] - rlv)
        maxtupla = self.Plr.maxVMGtwa(self.TW[1], math.copysign(twabrg, 1))
        return math.copysign(maxtupla[1], twabrg)

    def VMGTWD(self):
        return self.Speed() * math.cos(self.TWA)

    def AW(self):
        TWA = math.copysign(self.TWA, 1)
        TWS = self.TW[1]
        SPEED = self.Speed()
        aw = AW(TWS, TWA, SPEED)
        # AWSy=TWS*math.cos(TWA)+SPEED
        # AWSx=TWS*math.sin(TWA)
        # AWS=(AWSy**2+AWSx**2)**0.5
        # AWA=math.pi/2-math.atan2(AWSy,AWSx)
        # aw=(AWS,AWA)
        if self.TWA < 0:
            aw = (aw[0], -aw[1])
        return aw

    def StampaLat(self):
        return stampalat(self.Pos[0])

    def StampaLon(self):
        return stampalon(self.Pos[1])

    def Ruota(self):
        iconaruotata = []
        for punto in self.Icona:
            iconaruotata.append(ruota(punto, self.HDG()))
        fiocco = self.Fiocco()
        fioccoruotato = []
        for punto in fiocco:
            fioccoruotato.append(ruota(punto, self.HDG()))
        randa = self.Randa()
        randaruotata = []
        for punto in randa:
            randaruotata.append(ruota(punto, self.HDG()))
        return iconaruotata, fioccoruotato, randaruotata

    def StampaPolar(self):
        polare = []
        for twa in range(0, 185, 5):
            twa = math.radians(twa)
            speed = self.Plr.Speed(self.TW[1], twa)
            if self.TWA < 0:  # mure a sx
                x = speed * math.sin(twa)
                y = speed * math.cos(twa)
            else:  # mure a dx
                x = -speed * math.sin(twa)
                y = speed * math.cos(twa)
            polare.append((x, y))
        return polare

    def Fiocco(self):
        fiocco = []
        aw = self.AW()
        awa = aw[1]
        if awa > 0:
            segno = 1
        else:
            segno = -1
        awa = math.copysign(awa, 1)
        if awa > math.radians(90):
            l = 200
            zero = 165
            x0 = -(165 - 125) * segno * math.cos(awa)
            y0 = (165 - 125) * math.sin(awa)
        elif awa > math.radians(60):
            l = 145.0
            zero = 135
            x0 = 0
            y0 = 0
        else:
            l = 90
            zero = 125
            x0 = 0
            y0 = 0
    # if math.copysign(awa,1)<math.radians(25):
        if self.Speed() <= 0 or awa < math.radians(15):
            fiocco = [(0, 125.0), (0, 35.0)]
        else:
            r = l / awa
            cx = +segno * r * math.cos(awa)
            cy = zero - r * math.sin(awa)
            fine = int(math.degrees(awa) + 0.5)
            for angolo in range(0, fine):
                angolo = math.radians(angolo)
                x = cx - segno * r * math.cos(angolo) + x0
                y = cy + r * math.sin(angolo) + y0
                fiocco.append((x, y))
        return fiocco

    def Randa(self):
        aw = self.AW()
        awa = aw[1]
        randa = []
        if awa > 0:
            segno = 1
        else:
            segno = -1
        awa = math.copysign(awa, 1)
        l = 110
        zero = 35
        alfa0 = 10  # integer
        r = 0.5 * l / math.tan(math.radians(alfa0))
        if self.Speed() <= 0 or awa <= math.radians(alfa0):
            randa = [(0, 35.0), (0, -75.0)]
        else:
            beta = awa - math.radians(5)
            if beta > 0.5 * math.pi:
                beta = 0.5 * math.pi
            cx = segno * r * math.cos(beta + math.radians(alfa0))
            cy = zero - r * math.sin(beta + math.radians(alfa0))
            betaint = int(math.degrees(beta) + 0.5)
            for angolo in range(betaint - alfa0, betaint + alfa0):
                angolo = math.radians(angolo)
                x = cx - r * segno * math.cos(angolo)
                y = cy + r * math.sin(angolo)
                randa.append((x, y))
        return randa


# FUNZIONI
def cfbinomiale(n, i):
    return math.factorial(n) / (math.factorial(n - i) * math.factorial(i))


def AW(TWS, TWA, Speed):
    if TWA == 0.0:
        AWS = TWS
        AWA = TWA
    else:
        AWSy = TWS * math.cos(TWA) + Speed
        AWSx = TWS * math.sin(TWA)
        AWS = (AWSy**2 + AWSx**2)**0.5
        AWA = math.pi / 2 - math.atan2(AWSy, AWSx)
    return AWS, AWA


def ruota(punto, angle):
    ro = (punto[0]**2 + punto[1]**2)**0.5
    teta = math.atan2(punto[0], punto[1])
    teta = teta + angle
    puntoruotato = (ro * math.sin(teta), ro * math.cos(teta))
    return puntoruotato


def testmodulo():
    MaVie = Barca(polar_file="POL/PolareMini.pol")
    # variabili indipendenti
    MaVie.TW = (math.radians(45), 16)  # 1
    MaVie.TWA = math.radians(60)  # 3
    MaVie.Pos = (math.radians(42), math.radians(12))
    print "TWD: ", math.degrees(MaVie.TW[0])
    print "TWS: ", MaVie.TW[1]
    print "TWA: ", math.degrees(MaVie.TWA)
    print "Speed: ", MaVie.Speed()
    print "HDG: ", math.degrees(MaVie.HDG())
    print "VMGTWD: ", MaVie.VMGTWD()
    print "AWS: ", MaVie.AW()[0], "AWA: ", math.degrees(MaVie.AW()[1])
    print "lat: ", MaVie.StampaLat(), "lon: ", MaVie.StampaLon()
    print "Log: ", MaVie.Log
    print "Dist WP: ", MaVie.Dist(MIOWP)
    print "BRG WP: ", math.degrees(MaVie.BRG(MIOWP))
    print "VMGWP: ", MaVie.VMGWP(MIOWP)
    print "CMG: per rlv=40", MaVie.CMG(math.radians(40))
    print "TWAmaxCMG: per rlv=40", math.degrees(MaVie.TWAmaxCMG(math.radians(
        40)))
    MaVie.Muovi(5)  # metodo muovi
    print "Muovi per 5 secondi"
    print "lat: ", MaVie.StampaLat(), "lon: ", MaVie.StampaLat()
    print "Log: ", MaVie.Log
    print "Dist WP: ", MaVie.Dist(MIOWP)
    print "BRG WP: ", math.degrees(MaVie.BRG(MIOWP))
    print "VMGWP: ", MaVie.VMGWP(MIOWP)
    dati = []
    for alfa in range(0, 181, 1):
        alfa = math.radians(alfa)
        tupla = MaVie.Plr.maxVMGtwa(16.0, alfa)
        print math.degrees(alfa), tupla[0], math.degrees(tupla[1])


'''
#main
testmodulo()
'''
