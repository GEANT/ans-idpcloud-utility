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

### CONSTANTS
IDP_LOGOS="/opt/idpcloud-data/ansible-shibboleth/roles/idp/files/restore"
PLA_LOGO="/opt/idpcloud-data/ansible-shibboleth/roles/phpldapadmin/files/restore"
LINK_YML_DEST="/opt/ansible-shibboleth/inventories/production/host_vars"

### FUNCTIONS TO CREATE IDP YAML FILE ###

def get_random_color():
   return "#%06x" % random.randint(0, 0xFFFFFF)

def get_random_str(string_length):
   """Returns a random string of length string_length."""
   random = hashlib.sha256(str(uuid.uuid4())).hexdigest() # Generate SHA256.
   return random[0:string_length] # Return the random string.

def get_basedn_from_domain(domain):
   return "dc="+domain.replace(".",",dc=")

def create_idp_yml(idp_fqdn, ca_dest, yml_dest, idp_sealer_keystore_pw):
   yml_file = yml_dest + '/' + idp_fqdn + ".yml"
   if (path.isfile(yml_file)):
      print("IDP YAML FILE ALREADY CREATED:\n%s" % (yml_file))
   else:
      question_dict = OrderedDict([
         ("mdui_displayName_it","Insert the Institution Name for the ITALIAN language: "),
         ("mdui_displayName_en","Insert the Institution Name for the ENGLISH language: "),
         ("domain","Insert the Institution domain: "),
         ("org_url_it","Insert the Institution site for the ITALIAN language: "),
         ("org_url_en","Insert the Institution site for the ENGLISH language: "),
         ("mdui_logo_it","Insert the URL HTTPS of the Institution Logo (160x120) for the ITALIAN language (press Enter to keep the default value): "),
         ("mdui_logo_en","Insert the URL HTTPS of the Institution Logo (160x120) for the ENGLISH language (press Enter to keep the default value): "),
         ("mdui_favicon_it","Insert the URL HTTPS of the Institution Favicon (32x32) for the ITALIAN language (press Enter to keep the default value): "),
         ("mdui_favicon_en","Insert the URL HTTPS of the Institution Favicon (32x32) for the ENGLISH language (press Enter to keep the default value): "),
         ("footer_bkgr_color","Insert the hexadecimal color of the institution (press Enter to generate a random value): "),
         ("mdui_description_it","Insert Institution IdP description for the ITALIAN language (press Enter to keep the default value): "),
         ("mdui_description_en","Insert Institution IdP description for the ENGLISH language (press Enter to keep the default value): "),
         ("mdui_privacy_it","Insert the URL of the Privacy Policy page valid for the Institution in ITALIAN language (press Enter to keep the default value): "),
         ("mdui_privacy_en","Insert the URL of the Privacy Policy page valid for the Institution in ENGLIS language (press Enter to keep the default value): "),
         ("mdui_info_it","Insert the URL of the Information page valid for the Institution in ITALIAN language (press Enter to keep the default value): "),
         ("mdui_info_en","Insert the URL of the Information page valid for the Institution in ENGLISH language (press Enter to keep the default value): "),
         ("idp_support_email","Insert the User Support e-mail address for the Institutional IdP (press Enter to keep the default value 'idpcloud-service@example.org'): "),
         ("idp_support_address","Insert the Institutional street address (press Enter to keep the default value 'missing address'): "),
         ("ca","1) TERENA_SSL_CA_2\n2) TERENA_SSL_CA_3\n\nChoose 1 or 2 (or press Enter for 'TERENA_SSL_CA_3'): "),
         ("idp_persistentId_salt","Insert the persistent-id salt (press Enter to generate a random value): "),
         ("idp_fticks_salt","Insert the f-ticks salt (press Enter to generate a random value): "),
         ("web_gui_user","Insert the username of the user who will have access to the IdP IDM (press Enter to keep the default value 'idm-admin'): "),
         ("web_gui_pw","Insert the password of the user who will have access to the IdP IDM (press Enter to generate a random value): "),
         ("root_ldap_pw","Insert the openLDAP root password (press Enter to generate a random value): "),
         ("mysql_root_password","Insert the MySQL root password (press Enter to generate a random value): "),
         ("shibboleth_db_password","Insert the 'shibboleth' user password (press Enter to generate a random value): "),
         ("bindDNCredential","Insert the 'idpuser' user password (press Enter to generate a random value): "),
         ("idp_stats_db_pw","Insert the 'statistics' user password (press Enter to generate a random value): "),
         ("flup_secret_key","Insert the secret key used by FLUP (press Enter to generate a random value): "),
         ("idpcloud_idm","Insert 'spuid' to use 'schacPersonalUniqueID' or\nInsert 'email' to use the email address\nto recognize the user on the FLUP application (press Enter to keep 'spuid'): "),
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
            # Caso del logo IT predefinito
            elif(key == "mdui_logo_it" and (result == "" or result == None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/it'])
               call(["mkdir","-p",PLA_LOGO +'/'+idp_fqdn+'/images'])

               url = "https://garr-idp-prod.irccs.garr.it/it/logo.png"
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/it/logo.png', 'wb') as f:
                  f.write(r.content)

               with open(PLA_LOGO + '/' + idp_fqdn + '/images/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/it/logo.png"
            # Caso del logo IT fornito
            elif(key == "mdui_logo_it" and (result != "" or result != None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/it'])
               call(["mkdir","-p",PLA_LOGO +'/'+idp_fqdn+'/images'])

               url = result
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/it/logo.png', 'wb') as f:
                  f.write(r.content)

               with open(PLA_LOGO + '/' + idp_fqdn + '/images/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/it/logo.png"
            # Caso del logo EN predefinito
            elif(key == "mdui_logo_en" and (result == "" or result == None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/en'])

               url = "https://garr-idp-prod.irccs.garr.it/en/logo.png"
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/en/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/en/logo.png"
            # Caso del logo EN fornito
            elif(key == "mdui_logo_en" and (result != "" or result != None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/en'])

               url = result
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/en/logo.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/en/logo.png"
            # Cado della favicon IT predefinita
            elif(key == "mdui_favicon_it" and (result == "" or result == None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/it'])
               call(["mkdir","-p",PLA_LOGO +'/'+idp_fqdn+'/images'])

               url = "https://garr-idp-prod.irccs.garr.it/it/favicon.png"
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/it/favicon.png', 'wb') as f:
                  f.write(r.content)

               with open(PLA_LOGO + '/' + idp_fqdn + '/images/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/it/favicon.png"
            # Caso della favicon IT fornita
            elif(key == "mdui_favicon_it" and (result != "" or result != None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/it'])
               call(["mkdir","-p",PLA_LOGO +'/'+idp_fqdn+'/images'])

               url = result
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/it/favicon.png', 'wb') as f:
                  f.write(r.content)

               with open(PLA_LOGO + '/' + idp_fqdn + '/images/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/it/favicon.png"
            # Caso della favicon EN predefinita
            elif(key == "mdui_favicon_en" and (result == "" or result == None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/en'])

               url = "https://garr-idp-prod.irccs.garr.it/en/favicon.png"
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/en/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/en/favicon.png"
            # Cado della favicon EN fornita
            elif(key == "mdui_favicon_en" and (result != "" or result != None)):
               call(["mkdir","-p",IDP_LOGOS +'/'+idp_fqdn+'/styles/en'])

               url = result
               r = requests.get(url)
               with open(IDP_LOGOS + '/' + idp_fqdn + '/styles/en/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+idp_fqdn+"/en/favicon.png"
            elif(key == "idp_support_email" and (result == "" or result == None)):
               result = "idpcloud-service@example.org"
            elif(key == "idp_support_address" and (result == "" or result == None)):
               result = "missing address"
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

      # CREAZIONE YAML FILE PER L'IDP
      idp_yml = open(sys.path[0]+'/templates/createIDPyml.template', 'r').read()

      yaml = open(yml_dest + '/' + idp_fqdn + ".yml","w")
      yaml.write(Template(idp_yml).safe_substitute(vals))
      yaml.close()

      # POSIZIONA IL LINK NEL POSTO GIUSTO
      call(['ln','-s',PLA_LOGO + '/' + idp_fqdn, '/opt/ansible-shibboleth/roles/phpldapadmin/files/restore'])
      call(['ln','-s',yml_dest + '/' + idp_fqdn + ".yml", LINK_YML_DEST])

      # STAMPA "idm-admin" PASSWORD TO PROVIDE TO IDP MANAGER
      print("IDM User: %s\nIDM Password: %s\n" % (vals['web_gui_user'], vals['web_gui_pw']))
