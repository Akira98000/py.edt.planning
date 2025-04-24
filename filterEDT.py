#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DATE : 6/03/2023
# AUTEUR : ASANTHAKUMARAN

'# -*- coding: utf-8 -*-.'

import re
from datetime import datetime
import requests
import cgi
import time
import webbrowser
import urllib3


# UTILISATION DU GGI PLUS TARD LORS DE LA CREATION DE LA PAGE LOGIN
form = cgi.FieldStorage()
# On enleve cette erreur Casse Boule
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



unice_id = input("Nom D'utilisateur Université de Nice : ")
id = unice_id.upper()
url = f"https://iut-ical.unice.fr/gpucal.php?name={id}"
# On ne verifie pas le ssl, de toute facon on utilise pas le mot de passe
response = requests.get(url, verify=False) 
time.sleep(5)
with open('fichier.vcs', 'w') as fichier_vcs:
    fichier_vcs.write(response.text)


# Définir les expressions régulières pour chaque information à extraire
cn_pattern = re.compile(r'CN=([^\n]+)')
uid_pattern = re.compile(r'UID:([^\n]+)')
dtstart_pattern = re.compile(r'DTSTART;TZID=Europe/Paris:([^\n]+)')
dtend_pattern = re.compile(r'DTEND;TZID=Europe/Paris:([^\n]+)')
location_pattern = re.compile(r'LOCATION:([^\n]+)')
summary_pattern = re.compile(r'SUMMARY:([^\n]+)')
description_pattern = re.compile(r'DESCRIPTION:([^\n]+)')   
events = []
with open('fichier.vcs', 'r') as f:
     content = f.readlines()

event = {}
for line in content:
    if line.startswith('BEGIN:VEVENT'):
       event = {}
    elif line.startswith('END:VEVENT'):
        events.append(event)
    elif cn_pattern.search(line):
        cn = cn_pattern.search(line).group(1)
        event['CN'] = cn.split(':')[0]
    elif uid_pattern.search(line):
        uid = uid_pattern.search(line).group(1)
        event['UID'] = uid
    elif dtstart_pattern.search(line):
        dtstart = datetime.strptime(dtstart_pattern.search(line).group(1), '%Y%m%dT%H%M%S')
        event['DTSTART'] = dtstart
    elif dtend_pattern.search(line):
        dtend = datetime.strptime(dtend_pattern.search(line).group(1), '%Y%m%dT%H%M%S')
        event['DTEND'] = dtend
    elif location_pattern.search(line):
        location = location_pattern.search(line).group(1)
        event['LOCATION'] = location
    elif summary_pattern.search(line):
        summary = summary_pattern.search(line).group(1)
        event['SUMMARY'] = summary
    elif description_pattern.search(line):
        description = description_pattern.search(line).group(1)
        event['DESCRIPTION'] = description

# Ouvrir le fichier HTML en écriture
with open('edt_unice.html', 'w') as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('<meta charset="UTF-8">\n')
    f.write('<title>Emploi du temps</title>\n')
    f.write('<link rel="stylesheet" href="style.css">')
    f.write('</head>\n')
    f.write('<body>\n')
    # Ajouter le contenu de la page
    f.write('<header>\n')
    f.write("<h1>UNICE GPU EDT </h1>\n")
    f.write(f"<h2>IDENTIFIANT CONNECTÉE : {id}</h2>\n")
    f.write('<nav>\n')
    f.write('<a href="#">GPU EDT</a>\n')
    f.write('<a href="#">NOTE</a>\n')
    f.write('<a href="#">MOODLE</a>\n')
    f.write('</nav>\n')
    f.write('</header>\n')
    # Ajouter le contenu de l'emploi du temps
    events = sorted(events, key=lambda event: event['DTSTART'])
    days = {}
    for event in events:
        day = event['DTSTART'].strftime('%A %d %B %Y')
        if day not in days:
            days[day] = []
        days[day].append(event)
    
    for day, events in days.items():
        # On change les noms de dates défini par default en anglais en Francais, pareil pour les mois
        day = day.replace('Monday', 'Lundi')
        day = day.replace('Tuesday', 'Mardi')
        day = day.replace('Wednesday', 'Mercredi')
        day = day.replace('Thursday', 'Jeudi')
        day = day.replace('Friday', 'Vendredi')
        
        day = day.replace('January', 'Janvier')
        day = day.replace('February ', 'Février')
        day = day.replace('March', 'Mars')
        day = day.replace('April', 'Avril')
        day = day.replace('May', 'Mai')
        day = day.replace('June', 'Juin')
        day = day.replace('September', 'Septembre')
        day = day.replace('October', 'Octobre')
        day = day.replace('November', 'Novembre')
        day = day.replace('December', 'Decembre')

        
        
        f.write('<h1>' + day + '</h1>\n')
        f.write('<table>\n')
        f.write('<tr><th>Heure</th><th>Cours</th><th>Salle</th></tr>\n')
        for event in events:
            f.write('<tr>\n')
            f.write('<td>' + event['DTSTART'].strftime('%H:%M') + ' - ' + event['DTEND'].strftime('%H:%M') + '</td>\n')
            f.write('<td>' + event['SUMMARY'] + '</td>\n')
            f.write('<td>' + event.get('LOCATION', '') + '</td>\n')
            f.write('</tr>\n')
        f.write('</table>\n')
    
    # Ajouter le footer
    f.write('<footer>\n')
    f.write(f"<p>Emploi du Temps de {id}, crée par &copy; SANTHAKUMARAN</p>\n")
    f.write('</footer>\n')
    # Fermer la balise body et HTML
    f.write('</body>\n')
    f.write('</html>\n')
