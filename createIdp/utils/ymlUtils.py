#!/usr/bin/env python
# coding=utf-8

from string import Template
from base64 import b64encode
import os
from os import path 
import random
import sys
import requests
from subprocess import check_output,call
import uuid
import hashlib
import utils

### FUNCTIONS NEEDED TO CREATE IDP YAML FILE ###

def get_random_color():
   return "#%06x" % random.randint(0, 0xFFFFFF)

def get_random_str(string_length):
   """Returns a random string of length string_length."""
   random = hashlib.sha256(str(uuid.uuid4())).hexdigest() # Generate SHA256.
   return random[0:string_length] # Return the random string.

def get_basedn_from_domain(domain):
   return "dc="+domain.replace(".",",dc=")

def create_idp_yml(idp_fqdn, idp_entityID, ca_dest, yml_dest, data_ans_shib, ans_shib, idp_sealer_keystore_pw, ans_vault_file):
   yml_file = yml_dest + '/' + idp_fqdn + ".yml"

   if (path.isfile(yml_file)):
      print("\nIDP YAML FILE ALREADY EXISTS: %s" % (yml_file))
   else:
      question_dict = get_yml_orderedDict('it-IT')

      vals = {}

      vals['fqdn'] = idp_fqdn

      if(idp_entityID):
         vals['entityID'] = idp_entityID
      else:
         vals['entityID'] = "https://" + idp_fqdn + "/idp/shibboleth"

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
            elif(key == "idp_type" and (result == "" or result == None)):
               result = "Debian-IdP-with-IdM-GARR"
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

      ## Encrypt password with Ansible Vault
      # Needed to avoid output of 'call' commands
      FNULL = open(os.devnull, 'w')
      call(["ansible-vault", "encrypt", idp_fqdn+".yml", "--vault-password-file", ans_vault_file], cwd=yml_dest, stdout=FNULL)
      FNULL.close()

      # Print the "idm-admin" password to provide it to the IdP Manager
      print("IDM User: %s\nIDM Password: %s\n" % (vals['web_gui_user'], vals['web_gui_pw']))

      return vals['idp_type']
