#!/usr/bin/env python
# coding=utf-8

from string import Template
from base64 import b64encode
from os import urandom
import random
from os import path 
import sys
from collections import OrderedDict
import requests
from subprocess import check_output,call
import uuid
import hashlib

### FUNCTIONS NEEDED TO CREATE IDP YAML FILE ###

def get_random_color():
   return "#%06x" % random.randint(0, 0xFFFFFF)

def get_random_str(string_length):
   """Returns a random string of length string_length."""
   random = hashlib.sha256(str(uuid.uuid4())).hexdigest() # Generate SHA256.
   return random[0:string_length] # Return the random string.

def get_basedn_from_domain(domain):
   return "dc="+domain.replace(".",",dc=")

def create_idp_yml(idp_fqdn, ca_dest, yml_dest, data_ans_shib, ans_shib, idp_sealer_keystore_pw):
   yml_file = yml_dest + '/' + idp_fqdn + ".yml"

   if (path.isfile(yml_file)):
      print("\nIDP YAML FILE ALREADY EXISTS: %s" % (yml_file))
   else:
      question_dict = OrderedDict([
         ("mdui_displayName_it","Inserisci il nome dell'istituzione in ITALIANO: "),
         ("mdui_displayName_en","Inserisci il nome dell'istituzione in INGLESE: "),
         ("domain","Inserisci il dominio dell'istituzione: "),
         ("org_url_it","Inserisci il sito istituzionale pubblico in ITALIANO: "),
         ("org_url_en","Inserisci il sito istituzionale pubblico in INGLESE: "),
         ("mdui_logo_it","Inserisci la URL HTTPS del Logo ITALIANO(160x120) dell'istituzione (premi invio per tenere il valore predefinito): "),
         ("mdui_logo_en","Inserisci la URL HTTPS del Logo INGLESE(160x120) dell'istituzione (premi invio per tenere il valore predefinito): "),
         ("mdui_favicon_it","Inserisci la URL HTTPS della Favicon ITALIANA (32x32) dell'istituzione (premi invio per tenere il valore predefinito): "),
         ("mdui_favicon_en","Inserisci la URL HTTPS della Favicon INGLESE (32x32) dell'istituzione (premi invio per tenere il valore predefinito): "),
         ("footer_bkgr_color","Inserisci il colore esadecimale rappresentativo dell'istituzione (premi invio per generare un valore casuale): "),
         ("mdui_description_it","Inserisci la descrizione dell'IdP istituzionale in lingua ITALIANA (premi invio per tenere il valore predefinito): "),
         ("mdui_description_en","Inserisci la descrizione dell'IdP istituzionale in lingua INGLESE (premi invio per tenere il valore predefinito ): "),
         ("mdui_privacy_it","Inserisci la pagina di Privacy Policy per l'IdP in ITALIANO (premi invio per tenere il valore predefinito): "),
         ("mdui_privacy_en","Inserisci la pagina di Privacy Policy per l'IdP in INGLESE (premi invio per tenere il valore predefinito): "),
         ("mdui_info_it","Inserisci la pagina Informativa per l'IdP in ITALIANO (premi invio per tenere il valore predefinito): "),
         ("mdui_info_en","Inserisci la pagina Informativa per l'IdP in INGLESE (premi invio per tenere il valore predefinito): "),
         ("idp_support_email","Inserisci la mail di supporto per gli utenti dell'IdP istituzionale (premi invio per tenere il valore 'idpcloud-service@garr.it'): "),
         ("idp_support_address","Inserisci l'indirizzo postale dell'istituzione (premi invio per inserire in futuro: "),
         ("ca","1) TERENA_SSL_CA_2\n2) TERENA_SSL_CA_3\n\nScegli 1 o 2 (o premi INVIO 'TERENA_SSL_CA_3'): "),
         ("idp_persistentId_salt","Inserisci il persistent-id salt da applicare (premi invio per generare un valore casuale): "),
         ("idp_fticks_salt","Inserisci il salt per gli f-ticks da applicare (premi invio per generare un valore casuale): "),
         ("web_gui_user","Inserisci il nome dell'utente che accederà via Web l'IDM dell'IdP (premi invio per tenere il valore predefinito 'idm-admin'): "),
         ("web_gui_pw","Inserisci la password dell'utente che accederà via web all'IDM dell'IdP (premi invio per generare un valore casuale): "),
         ("root_ldap_pw","Inserisci la password dell'utente 'admin' di openLDAP (premi invio per generare un valore casuale): "),
         ("mysql_root_password","Inserisci la password dell'utente 'root' di MySQL (premi invio per generare un valore casuale): "),
         ("shibboleth_db_password","Inserisci la password dell'utente 'shibboleth' di MySQL (premi invio per generare un valore casuale): "),
         ("bindDNCredential","Inserisci la password dell'utente 'idpuser' di OpenLDAP (premi invio per generare un valore casuale): "),
         ("idp_stats_db_pw","Inserisci la password dell'utente 'statistics' di MySQL (premi invio per generare un valore casuale): "),
         ("flup_secret_key","Inserisci la secret key di FLUP (premi invio per generare un valore casuale): "),
         ("idpcloud_idm","Inserisci 'spuid' per riconoscere gli utenti con il Codice Fiscale(schacPersonalUniqueID) o\nInserisci 'email' per riconoscere gli utenti con la loro e-mail personale (premi invio per 'spuid'): "),
      ])

      vals = {}

      vals['fqdn'] = idp_fqdn

      for key,question in question_dict.iteritems():

         result = ""

         while (result == "" or result == None):
            result = raw_input(question)

            if(key == "ca"):
               if (result == "1"):
                  url = "https://www.terena.org/activities/tcs/repository/sha2/TERENA_SSL_CA_2.pem"
                  result = "TERENA_SSL_CA_2.pem"
               else:
                  url = "https://www.terena.org/activities/tcs/repository-g3/TERENA_SSL_CA_3.pem"
                  result = "TERENA_SSL_CA_3.pem"
               r = requests.get(url)
               with open(ca_dest + '/' + result, 'wb') as f:
                  f.write(r.content)
            elif(key == "domain"):
               vals['basedn'] = get_basedn_from_domain(result)
            elif(key == "mdui_description_it" and (result == "" or result == None)):
               result = "Identity provider per gli utenti di "+vals['mdui_displayName_it']
            elif(key == "mdui_description_en" and (result == "" or result == None)):
               result = "Identity provider for "+vals['mdui_displayName_en']+" users"
            elif(key == "mdui_privacy_it" and (result == "" or result == None)):
               result = "https://"+idp_fqdn+"/it/privacy.html"
            elif(key == "mdui_privacy_en" and (result == "" or result == None)):
               result = "https://"+idp_fqdn+"/en/privacy.html"
            elif(key == "mdui_info_it" and (result == "" or result == None)):
               result = "https://"+idp_fqdn+"/it/info.html"
            elif(key == "mdui_info_en" and (result == "" or result == None)):
               result = "https://"+idp_fqdn+"/en/info.html"
            # CASE 1: Default Italian Logo
            elif(key == "mdui_logo_it" and (result == "" or result == None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it'])
               call(["mkdir","-p",data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images'])

               url = "https://garr-idp-prod.irccs.garr.it/it/logo.png"
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it/logo.png', 'wb') as f:
                  f.write(r.content)

               with open(data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/it/logo.png"
            # CASE 2: Italian Logo provided by the institution via HTTP/HTTPS location
            elif(key == "mdui_logo_it" and (result != "" or result != None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it'])
               call(["mkdir","-p",data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images'])

               url = result
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it/logo.png', 'wb') as f:
                  f.write(r.content)

               with open(data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/it/logo.png"
            # CASE 3: Default English Logo
            elif(key == "mdui_logo_en" and (result == "" or result == None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en'])

               url = "https://garr-idp-prod.irccs.garr.it/en/logo.png"
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/en/logo.png"
            # CASE 4: English Logo provided by the institution via HTTP/HTTPS location
            elif(key == "mdui_logo_en" and (result != "" or result != None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en'])

               url = result
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/en/logo.png"
            # CASE 5: Default Italian Favicon
            elif(key == "mdui_favicon_it" and (result == "" or result == None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it'])
               call(["mkdir","-p",data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images'])

               url = "https://garr-idp-prod.irccs.garr.it/it/favicon.png"
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it/favicon.png', 'wb') as f:
                  f.write(r.content)

               with open(data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/it/favicon.png"
            # CASE 6: Italian Favicon provided by the institution via HTTP/HTTPS location
            elif(key == "mdui_favicon_it" and (result != "" or result != None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore' +'/'+idp_fqdn+'/styles/it'])
               call(["mkdir","-p",data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images'])

               url = result
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/it/favicon.png', 'wb') as f:
                  f.write(r.content)

               with open(data_ans_shib +'/roles/phpldapadmin/files/restore/'+ idp_fqdn +'/images/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/it/favicon.png"
            # CASE 7: Default English Favicon
            elif(key == "mdui_favicon_en" and (result == "" or result == None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en'])

               url = "https://garr-idp-prod.irccs.garr.it/en/favicon.png"
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/en/favicon.png"
            # CASE 8: English Favicon provided by the institution via HTTP/HTTPS location
            elif(key == "mdui_favicon_en" and (result != "" or result != None)):
               call(["mkdir","-p",data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en'])

               url = result
               r = requests.get(url)
               with open(data_ans_shib +'/roles/idp/files/restore/'+ idp_fqdn +'/styles/en/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/en/favicon.png"
            elif(key == "idp_support_email" and (result == "" or result == None)):
               result = "idpcloud-service@garr.it"
            elif(key == "idp_support_address" and (result == "" or result == None)):
               result = "Mancante|Missing"
            elif(key == "footer_bkgr_color" and (result == "" or result == None)):
               result = get_random_color()
            elif(key == "idp_persistentId_salt" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "idp_fticks_salt" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "web_gui_user" and (result == "" or result == None)):
               result = "idm-admin"
            elif(key == "web_gui_pw" and (result == "" or result == None)):
               result = get_random_str(16)
            elif(key == "root_ldap_pw" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "mysql_root_password" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "shibboleth_db_password" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "bindDNCredential" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "idp_stats_db_pw" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "flup_secret_key" and (result == "" or result == None)):
               result = get_random_str(64)
            elif(key == "idpcloud_idm" and (result == "" or result == None)):
               result = "spuid"

         vals[key] = result

      vals['sealer_keystore_password'] = idp_sealer_keystore_pw

      # Create the IdP YAML file
      idp_yml = open(sys.path[0]+'/templates/createIDPyml.template', 'r').read()

      yaml = open(yml_dest + '/' + idp_fqdn + ".yml","w")
      yaml.write(Template(idp_yml).safe_substitute(vals))
      yaml.close()

      # Print the "idm-admin" password to provide it to the IdP Manager
      print("IDM User: %s\nIDM Password: %s\n" % (vals['web_gui_user'], vals['web_gui_pw']))
