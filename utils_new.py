#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk

import math
import os
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np

from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from hurry.filesize import size
import string
import time
import re

# Pliki z JPKami

#SAP HURT
files = os.listdir(r"\\...")

slownik = {
   'XYZ':
    {
        'nazwa':'',
        'pliki':'',
        'sciezka' : r"\\..."
    },  
}

# Listy do warunkow z zagranicznymi podmiotami
letters = list(string.ascii_uppercase)

kody_kraju = [
    'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ',
    'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BR', 'BS', 'BT',
    'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO',
    'CP', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE',
    'EG', 'EH', 'EL', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 
    'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM', 
    'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IN', 'IM', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 
    'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 
    'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 
    'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 
    'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 
    'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 
    'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 
    'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 
    'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UK', 'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 
    'VN', 'VU', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM', 'ZW'
]

def wspolne_podstringi(lista):
    """Funkcja wyszukująca wspólny najdłuższy podciąg znaków do wyabstrachowania 
    nazw kolumn w pliku xml"""
    
    if not lista:
        return None
    
    # Tworzymy zbiór zawierający wszystkie podłańcuchy z pierwszego słowa
    wspolne_podstringi = set()
    slowo_pierwsze = lista[0]
    for i in range(len(slowo_pierwsze)):
        for j in range(i + 1, len(slowo_pierwsze) + 1):
            wspolne_podstringi.add(slowo_pierwsze[i:j])
            
    # Sprawdzamy wspólne podłańcuchy dla pozostałych słów w liście
    for slowo in lista[1:]:
        nowe_wspolne_podstringi = set()
        for podslowo in wspolne_podstringi:
            if podslowo in slowo:
                nowe_wspolne_podstringi.add(podslowo)
        wspolne_podstringi = nowe_wspolne_podstringi
        
    # Sortujemy podłańcuchy wg długości w kolejności malejącej
    wspolne_podstringi = sorted(list(wspolne_podstringi), key=len, reverse=True)
    
    # Wybieramy tylko te o największej długości
    najdluzsze_podstringi = [x for x in wspolne_podstringi if len(x) == len(wspolne_podstringi[0])]
    
    return najdluzsze_podstringi

def check_files(pliki, kolumny_do_sprawdzenia):
    """ Funkcja sprawdzająca, filtrująca pliki i pozostawiająca te,
    gdzie występują wskazane w liście bądź osobno kolumny"""
    
    # Jeśli przeszukiwane kolumny nie są listą, to zmiana na listę
    if type(kolumny_do_sprawdzenia) != type(list()):
        kolumny_do_sprawdzenia = [kolumny_do_sprawdzenia]
            
    files_to_check = []
    
    # Jeśli w danym pliku znajduje się jedna z zadanych kolumn i liczba rekordów jest > 0, plik zostaje dodany do listy do przeszukania
    for file in pliki:
        tree = ET.parse(file[2]+'\\'+file[0])
        root = tree.getroot()
            
        Ps = [e for e in [elem.tag for elem in root.iter()] if any(s in str(e) for s in kolumny_do_sprawdzenia)]

        if len(Ps)>0: files_to_check.append(file)

    return files_to_check

def check_files_size(directory, input_files):
    """ Funkcja do sprawdzania wielkości plików wskazanych w ścieżce """
    size_files = []

    for file in input_files:
        file_size = os.path.getsize(directory+file)
        size_files.append([file, file_size, size(file_size)])

    return size_files

def flatten(l):
    """ Funkcja wypłaszczająca listę"""
    return [item for sublist in l for item in sublist]

def format_dat(miesiac, rok):
    """Funkcja do nadania przekazanym datom odpowiedniego formatu"""
    
    # Jeśli przeszukiwany jest cały rok
    try:
        if miesiac.upper() == 'ALL':
            miesiac = [i+1 for i in range(12)]
    except:
        pass
    
    # Zamiana na listy
    if type(miesiac) != type(list()):
        miesiac = [miesiac]
    if type(rok) != type(list()):
        rok = [rok]

    # Zamiana na stringi
    miesiac = [str(m) if type(m) != type('xyz') else m for m in miesiac]
    miesiac = ['0'+ m if len(m) < 2 else m for m in miesiac]
    rok = [str(r) if type(r) != type('xyz') else r for r in rok]

    # Lista z potencjalnymi formatami
    daty = []
    for r in rok:
        for m in miesiac:
            daty.append([r+m, m+r, r+'.'+m, m+'.'+r, r+'-'+m, m+'-'+r, r+' '+m, m+' '+r])
    return flatten(daty)

def lista_plikow(business_unity=None):
    """ Funkcja tworząca listę plików do przeszukania dla podanej listy business unitów"""
    if business_unity == 'ALL' or business_unity == 'all' or business_unity == 'All' or business_unity == None:
        business_unity = list(slownik.keys())
    else:
        if type(business_unity) != type(list()):
            business_unity = [business_unity]
    business_unity = [i.upper() for i in business_unity]
    
    pliki = [list(zip(eval(slownik[x]['pliki']),[slownik[x]['nazwa']]*len(eval(slownik[x]['pliki'])), [slownik[x]['sciezka']]*len(eval(slownik[x]['pliki'])))) for x in business_unity]
    # Wypłaszczenie listy
    pliki = flatten(pliki)
    
    return pliki

def filtruj_liste_plikow(lista_plikow, miesiac, rok):
    """ Funkcja filtrująca pliki po wprowadzonych wartościach daty"""
    pliki = [plik for plik in lista_plikow if (any(s in plik[0] for s in format_dat(miesiac = miesiac, rok = rok)) and ".xml" in plik[0])]
    return pliki

def pliki_ostatnie_wersje(pliki):
    """ Funkcja filtrująca redukująca listę plików do ich ostatnich wersji"""
    table = pd.DataFrame(pliki, columns=['Name file','BU', 'Path'])

    table['Version'] = table['Name file'].apply(lambda x: x[-5])
    table['Name'] = table['Name file'].apply(lambda x: x[:-7])
    table = table.groupby(by=['BU','Name'], as_index=False).max()
    table = table.drop('Name', axis=1)
    table = table[['Name file','BU', 'Path']]

    return table.to_records(index=False).tolist()
        
def podziel_liste(lista, slowo_klucz=None):
    """ Funkcja dzieląca listę słowników na podsłowniki podstawie klucza, który rozdziela każdy chunk"""
    lista_wynikowa = []
    podlista = []
    for slownik in lista:
        if slowo_klucz in slownik.keys():
            if podlista:
                lista_wynikowa.append(podlista)
                podlista = []
        podlista.append(slownik)
    if podlista:
        lista_wynikowa.append(podlista)
    return lista_wynikowa

def convert_list_of_dicts_to_dict(list_of_dicts):
    """ Funkcja do zmiany listy słowników w jeden słownik"""
    result_dict = {}
    for dictionary in list_of_dicts:
        result_dict.update(dictionary)
    return result_dict

def zwroc_ramke(lista, kolumny, warunki, slowo_klucz=None):
    """ Funkcja zwracjąca składowe tabele pliku xml"""
    wspolny = '{http://crd.gov.pl/wzor/2021/12/27/11148/}'
    data = [(pozycje[0][len(wspolny):], pozycje[1]) for rekordy in lista for pozycje in rekordy]
    lista_slownikow = [{tupla[0]: tupla[1]} for tupla in data]
    lista_podzielona = podziel_liste(lista_slownikow, slowo_klucz=slowo_klucz)
   
    try:
        if (kolumny == [None]) & (warunki != []):
            df = pd.concat([pd.DataFrame(convert_list_of_dicts_to_dict(i), index=[0]) for i in lista_podzielona 
                    if any(condition in i for condition in warunki)], axis=0)
        elif (kolumny != [None]) & (warunki == []):
            df = pd.concat([pd.DataFrame(convert_list_of_dicts_to_dict(i), index=[0]) for i in lista_podzielona 
                    if (any(wyraz in slownik for slownik in i for wyraz in kolumny)
                        & len([float(slownik.get(klucz)) for klucz in kolumny for slownik in i if klucz in slownik and float(slownik.get(klucz)) != 0]) > 0)], axis=0)
        elif (kolumny != [None]) & (warunki != []):
            df = pd.concat([pd.DataFrame(convert_list_of_dicts_to_dict(i), index=[0]) for i in lista_podzielona 
                    if (any(wyraz in slownik for slownik in i for wyraz in kolumny)
                        & len([float(slownik.get(klucz)) for klucz in kolumny for slownik in i if klucz in slownik and float(slownik.get(klucz)) != 0]) > 0)
                          & any(condition in i for condition in warunki)], axis=0)
        elif (kolumny == [None]) & (warunki == []):
            df = pd.concat([pd.DataFrame(convert_list_of_dicts_to_dict(i), index=[0]) for i in lista_podzielona], axis=0)
                            
    except:
        df = pd.DataFrame()

    return df

#### GŁÓWNA FUNKCJA ####

def funkcja_generująca_plik(rok, miesiac, kolumny ,nazwa_pliku, kontrahenci=None, BU=None, czarna_lista = False, zagranica = False, excel = False, s_wieksza_niz = float('-inf'), s_mniejsza_niz = float('inf'), z_wieksza_niz = float('-inf'), z_mniejsza_niz = float('inf') ): 
    """ Główna funkcja generująca plik zwracający rekordy dla interesujących użytkownika kolumn dla zadanego zakresu miesięcy"""
    
    ### Warunki nakładane w oknie dotyczące numerów NIP podmiotów i podmioty z zagranicy
    warunki = []

    if type(kontrahenci) != type(list()):
        kontrahenci = [kontrahenci]
    if kontrahenci != [None]:
        nazwy_kluczy = ['NrDostawcy', 'NrKontrahenta']
        warunki = warunki + [{k: nr} for nr, k in zip(kontrahenci * len(nazwy_kluczy), nazwy_kluczy * len(kontrahenci))]

    if zagranica == True:
        combinations = [{'KodKrajuNadaniaTIN': kk} for kk in kody_kraju if kk != 'PL'] # Wszystkie kombinacje dwuliterowe bez PL
        warunki = warunki + combinations
    
    ###
    
    # Dopilnowanie by kolumny były listą
    if type(kolumny) != type(list()):
        kolumny = [kolumny]
    
    # lista plików do wyciągnięcia wartości
    pliki = pliki_ostatnie_wersje(filtruj_liste_plikow(lista_plikow(BU), miesiac = miesiac, rok=rok))
        
    # do zakładki sprzedaz
    tab_sprzedaz = []
    # do zakładki zakup
    tab_zakup = []

    # Zależy nam tylko na tabelkach "SprzedazWiersz" i "ZakupWiersz"
    for plik in pliki:

        # Wczytanie drzewa
        tree = ET.parse(f"{plik[2]}\{plik[0]}")
        root = tree.getroot()
        
        # Sprawdzenie, czy drzewo zawiera kolumnę
        if kolumny != [None]:
            Ps = [e for e in [elem.tag for elem in root.iter()] if any(s in str(e) for s in kolumny)]
        else:
            Ps = 'Kolumny w pliku'
        
        # Jeśli zawiera to rozpoczynamy zaczytywanie danych
        if len(Ps)>0:

            # Puste listy na rekordy
            sprzedaz_wiersze = [] 
            zakup_wiersze = []

            for child in root:
                if child.tag.endswith("Ewidencja"):
                    for ewidencja_child in child:
                        if ewidencja_child.tag.endswith("SprzedazWiersz"):
                            row_data_sprzed_wiersze = {}  # Słownik na dane jednego wiersza
                            for sprzedaz_wiersz_child in ewidencja_child:
                                if sprzedaz_wiersz_child.text is not None and sprzedaz_wiersz_child.text != '':
                                    row_data_sprzed_wiersze[sprzedaz_wiersz_child.tag] = sprzedaz_wiersz_child.text
                            sprzedaz_wiersze.append(tuple(row_data_sprzed_wiersze.items()))  
                        elif ewidencja_child.tag.endswith("ZakupWiersz"):
                            row_data_zakup_wiersze = {}  # Słownik na dane jednego wiersza
                            for zakup_wiersz_child in ewidencja_child:
                                if zakup_wiersz_child.text is not None and zakup_wiersz_child.text != '':
                                    row_data_zakup_wiersze[zakup_wiersz_child.tag] = zakup_wiersz_child.text
                            zakup_wiersze.append(tuple(row_data_zakup_wiersze.items())) 

            # Zwrócenie kolumn z informacjami o dokumencie i zadeklarowanych kolumn
            try:
                s = zwroc_ramke(sprzedaz_wiersze, kolumny, warunki, 'LpSprzedazy')

                # Jeśli sprawdzamy GTU, to zwracamy wszystkie kolumny, jak nie to tylko te zadeklarowane
                if (kolumny != [None] and any('GTU' in word for word in kolumny)) | (kolumny == [None]):
                    sprzedaz = s
                else:
                    sprzedaz = s.filter(items=[col for col in s.columns if not any(char.isdigit() for char in col)] + kolumny)

                # Czarna lista
                if czarna_lista == True:
                    sprzedaz = sprzedaz[sprzedaz.NrKontrahenta.astype(str).isin(czarna)]

                for k in list(sprzedaz.filter(regex=r'\d+').columns):
                    try:
                        sprzedaz[k] = sprzedaz[k].astype(float)
                    except: 
                        pass

                # Warunki wartościowe
                col_s = list(sprzedaz.filter(regex=r'\d+').columns)
                #col_s = [col for col in kolumny if col in sprzedaz.columns]
                maska_s = sprzedaz[col_s].ge(s_wieksza_niz) & sprzedaz[col_s].le(s_mniejsza_niz)
                maska_s = maska_s.any(axis=1)
                sprzedaz = sprzedaz[maska_s]

                # Dodanie (nazwa pliku, ścieżka, biznes)
                sprzedaz['Nazwa_pliku'] = plik[0]
                sprzedaz['Sciezka'] = plik[2]
                sprzedaz['BU'] = plik[1]

                tab_sprzedaz.append(sprzedaz)
            except:
                pass

            # Zwrócenie kolumn z informacjami o dokumencie i zadeklarowanych kolumn
            try:
                z = zwroc_ramke(zakup_wiersze, kolumny, warunki, 'LpZakupu')

                # Jeśli sprawdzamy GTU, to zwracamy wszystkie kolumny, jak nie to tylko te zadeklarowane
                if (kolumny != [None] and any('GTU' in word for word in kolumny)) | (kolumny == [None]):
                    zakup = z
                else:
                    zakup = z.filter(items=[col for col in z.columns if not any(char.isdigit() for char in col)] + kolumny)

                # Czarna lista
                if czarna_lista == True:
                    zakup = zakup[zakup.NrDostawcy.astype(str).isin(czarna)]

                for k in list(zakup.filter(regex=r'\d+').columns):
                    try:
                        zakup[k] = zakup[k].astype(float)
                    except: 
                        pass

                # Warunki wartościowe
                col_z = list(zakup.filter(regex=r'\d+').columns)
                #col_z = [col for col in kolumny if col in zakup.columns]
                maska_z = zakup[col_z].ge(z_wieksza_niz) & zakup[col_z].le(z_mniejsza_niz)
                maska_z = maska_z.any(axis=1)
                zakup = zakup[maska_z]

                # Dodanie (nazwa pliku, ścieżka, biznes)
                zakup['Nazwa_pliku'] = plik[0]
                zakup['Sciezka'] = plik[2]
                zakup['BU'] = plik[1]

                tab_zakup.append(zakup)
            except:
                pass
        else:
            pass

    # Tworzenie ramek wynikowych
    
    # Sprzedaz
    try:
        tab_sprzedaz = pd.concat(tab_sprzedaz)
    except:
        pass
    
    try:
        tab_sprzedaz.drop('LpSprzedazy', axis=1, inplace=True)
    except:
        pass
    
    # Zakup
    try:
        tab_zakup = pd.concat(tab_zakup)
    except:        
        pass
    
    try:
        tab_zakup.drop('LpZakupu', axis=1, inplace=True)
    except:
        pass
    
    # Zmiana kolejności kolumn
    
    cols_to_move = ['Nazwa_pliku', 'Sciezka', 'BU']
    
    try: 
        cols_dig_sprzed = [nazwa for nazwa in tab_sprzedaz.columns if any(char.isdigit() for char in nazwa)]
        new_cols_order_s = tab_sprzedaz.columns.difference(cols_dig_sprzed+cols_to_move).tolist() + cols_dig_sprzed + cols_to_move
        tab_sprzedaz = tab_sprzedaz.reindex(columns=new_cols_order_s)
    except:
        pass
    
    try:
        cols_dig_zakup = [nazwa for nazwa in tab_zakup.columns if any(char.isdigit() for char in nazwa)]
        new_cols_order_z = tab_zakup.columns.difference(cols_dig_zakup+cols_to_move).tolist() + cols_dig_zakup + cols_to_move
        tab_zakup = tab_zakup.reindex(columns=new_cols_order_z)
    except:
        pass
    
    if excel == True:
        # Zapisywanie wyników do excela
        writer = pd.ExcelWriter(f'{nazwa_pliku}.xlsx', engine = 'xlsxwriter')
        if len(tab_sprzedaz) > 0 :
            tab_sprzedaz.to_excel(writer, sheet_name = 'SprzedazWiersze', index = False)
        if len(tab_zakup) > 0:
            tab_zakup.to_excel(writer, sheet_name = 'ZakupWiersze', index = False)
        writer.close()
    elif excel == False:
        # Zapisywanie wyników do csv
        if len(tab_sprzedaz) > 0 :
            tab_sprzedaz.to_csv(f'{nazwa_pliku}_SprzedazWiersze.csv', encoding = 'utf8', sep=';', decimal = ',', index = False)
        if len(tab_zakup) > 0:
            tab_zakup.to_csv(f'{nazwa_pliku}_ZakupWiersze.csv', encoding = 'utf8', sep=';', decimal = ',', index = False)

    return len(tab_sprzedaz), len(tab_zakup)

