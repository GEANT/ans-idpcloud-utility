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
import validators
import logging

### FUNCTIONS NEEDED TO CREATE IDP YAML FILE ###

def get_random_color():
   return "#%06x" % random.randint(0, 0xFFFFFF)

def get_random_str(string_length):
   """Returns a random string of length string_length."""
   random = hashlib.sha256(str(uuid.uuid4())).hexdigest() # Generate SHA256.
   return random[0:string_length] # Return the random string.

def get_basedn_from_domain(domain):
   return "dc="+domain.replace(".",",dc=")

def create_idp_yml(idp_fqdn, idp_entityID, ca_dest, yml_dest, idp_styles_dir, idp_pla_files_dir, idp_sealer_keystore_pw, ans_vault_file):

   if (path.isfile(yml_dest)):
      logging.debug("IdP YAML file already exist at: %s" % (yml_dest))
   else:
      # Add language on 'utils/langUtils.py' file.
      #
      # Language Supported: 'it-IT','en-GB'
      question_dict = utils.get_yml_orderedDict('en-GB')

      vals = {}

      vals['fqdn'] = idp_fqdn

      if (idp_entityID):
         vals['entityID'] = idp_entityID
      else:
         vals['entityID'] = "https://" + idp_fqdn + "/idp/shibboleth"

      for key,question in question_dict.iteritems():

         result = ""

         while (result == "" or result == None):
            result = raw_input(question)

            if (key == "ca"):
               checkUrl = validators.url(result)
               while not(checkUrl == True):
                  result = raw_input(question)
                  checkUrl = validators.url(result)

               r = requests.get(result)
               with open(ca_dest + '/cacert.pem', 'wb') as f:
                  f.write(r.content)

            if(key == "domain"):
               checkUrl = validators.domain(result)
               while not(checkUrl == True):
                  result = raw_input(question)
                  checkUrl = validators.domain(result)

               vals['basedn'] = get_basedn_from_domain(result)
 
            if (key == 'org_url_it' or key == 'org_url_en'):
               checkUrl = validators.url(result)
               while not (checkUrl == True):
                  result = raw_input(question)
                  checkUrl = validators.url(result)

            if (key == "mdui_description_it" and (result == "" or result == None)):
               result = "Identity provider per gli utenti di " + vals['mdui_displayName_it']

            if (key == "mdui_description_en" and (result == "" or result == None)):
               result = "Identity provider for " + vals['mdui_displayName_en'] + " users"

            if (key == "mdui_privacy_it"):
               checkUrl = False
               while not (checkUrl == True):
                  if (result == "" or result == None):
                     result = "https://"+idp_fqdn+"/it/privacy.html"
                     checkUrl = True
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

            if (key == "mdui_privacy_en"):
               checkUrl = False
               while not (checkUrl == True):
                  if (result == "" or result == None):
                     result = "https://"+idp_fqdn+"/en/privacy.html"
                     checkUrl = True
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

            if (key == "mdui_info_it"):
               checkUrl = False
               while not (checkUrl == True):
                  if (result == "" or result == None):
                     result = "https://"+idp_fqdn+"/it/info.html"
                     checkUrl = True
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

            if (key == "mdui_info_en"):
               checkUrl = False
               while not (checkUrl == True):
                  if (result == "" or result == None):
                     result = "https://"+idp_fqdn+"/en/info.html"
                     checkUrl = True
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

            # Italian IdP Logo: 
            # It will be stored on the IdP storage
            # and will be available on "/it/logo.png" location
            if (key == "mdui_logo_it"):
               call(["mkdir","-p",idp_styles_dir + '/it'])

               checkUrl = False
               while not (checkUrl == True):
                  # CASE 1: Default
                  if (result == "" or result == None):
                    result = "https://garr-idp-prod.irccs.garr.it/it/logo.png"
                    checkUrl = True
                  # CASE 2: Logo provided by institution via HTTP/HTTPS url
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

               r = requests.get(result)
               with open(idp_styles_dir + '/it/logo.png', 'wb') as f:
                  f.write(r.content)
 
               result = "https://"+ idp_fqdn +"/it/logo.png"

            # English IdP & PLA Logo
            # It will be stored on the IdP storage
            # and will be available on "/en/logo.png" location
            if (key == "mdui_logo_en"):
               call(["mkdir","-p",idp_styles_dir + '/en'])
               call(["mkdir","-p",idp_pla_files_dir + '/images'])

               checkUrl = False
               while not (checkUrl == True):
                  # CASE 3: Default
                  if (result == "" or result == None):
                     result = "https://garr-idp-prod.irccs.garr.it/en/logo.png"
                     checkUrl = True
                  # CASE 4: Logo provided by institution via HTTP/HTTPS url
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

               r = requests.get(result)
               with open(idp_styles_dir + '/en/logo.png', 'wb') as f:
                  f.write(r.content)

               with open(idp_pla_files_dir + '/images/logo.png', 'wb') as f:
                  f.write(r.content)
             
               result = "https://"+ idp_fqdn +"/en/logo.png"

            # Italian IdP Favicon
            # It will be stored on the IdP storage
            # and will be available on "/it/favicon.png" location
            if (key == "mdui_favicon_it"):
               call(["mkdir","-p", idp_styles_dir + '/it'])

               checkUrl = False
               while not (checkUrl == True):
                  # CASE 5: Default
                  if (result == "" or result == None):
                     result = "https://garr-idp-prod.irccs.garr.it/it/favicon.png"
                     checkUrl = True
                  # CASE 6: Favicon provided by institution via HTTP/HTTPS url
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

               r = requests.get(result)
               with open(idp_styles_dir + '/it/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/it/favicon.png"

            # English IdP & PLA Favicon
            # It will be stored on the IdP storage
            # and will be available on "/en/favicon.png" location
            if (key == "mdui_favicon_en"):
               call(["mkdir","-p",idp_styles_dir + '/en'])
               call(["mkdir","-p",idp_pla_files_dir + '/images'])

               checkUrl = False
               while not (checkUrl == True):
                  # CASE 7: Default
                  if (result == "" or result == None):
                     result = "https://garr-idp-prod.irccs.garr.it/en/favicon.png"
                     checkUrl = True
                  # CASE 8: English Favicon provided by the institution via HTTP/HTTPS location
                  elif (validators.url(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

               r = requests.get(result)
               with open(idp_styles_dir + '/en/favicon.png', 'wb') as f:
                  f.write(r.content)

               with open(idp_pla_files_dir + '/images/favicon.png', 'wb') as f:
                  f.write(r.content)

               result = "https://"+ idp_fqdn +"/en/favicon.png"

            if(key == "idp_support_email"):
               checkUrl = False
               while not (checkUrl == True):
                  if (result == "" or result == None):
                     result = "Mancante|Missing"
                     checkUrl = True
                  elif (validators.email(result)):
                     checkUrl = True
                  else:
                     result = raw_input(question)

            if(key == "idp_support_address" and (result == "" or result == None)):
               result = "Mancante|Missing"

            if(key == "footer_bkgr_color" and (result == "" or result == None)):
               result = get_random_color()

            if(key == "idp_type" and (result == "" or result == None)):
               result = "Debian-IdP-with-IdM"

            if(key == "idp_persistentId_salt" and (result == "" or result == None)):
               result = get_random_str(64)

            if(key == "idp_fticks_salt" and (result == "" or result == None)):
               result = get_random_str(64)

            if(key == "web_gui_user" and (result == "" or result == None)):
               result = "idm-admin"

            if(key == "web_gui_pw" and (result == "" or result == None)):
               result = get_random_str(16)

            if(key == "root_ldap_pw" and (result == "" or result == None)):
               result = get_random_str(64)

            if(key == "mysql_root_password" and (result == "" or result == None)):
               result = get_random_str(64)

            if(key == "shibboleth_db_password" and (result == "" or result == None)):
               result = get_random_str(64)

            if(key == "bindDNCredential" and (result == "" or result == None)):
               result = get_random_str(64)

            if(key == "idp_stats_db_pw" and (result == "" or result == None)):
               result = get_random_str(64)

         vals[key] = result

      vals['sealer_keystore_password'] = idp_sealer_keystore_pw

      # Create the IdP YAML file
      idp_yml = open(sys.path[0]+'/templates/createIDPyml.template', 'r').read()

      yaml = open(yml_dest, "w")
      yaml.write(Template(idp_yml).safe_substitute(vals))
      yaml.close()

      ## Encrypt password with Ansible Vault (if requested)
      if (ans_vault_file):
         # Needed to avoid output of 'call' commands
         FNULL = open(os.devnull, 'w')
         call(["ansible-vault", "encrypt", yml_dest, "--vault-password-file", ans_vault_file], stdout=FNULL)
         FNULL.close()

      # Print the "idm-admin" password for the IdP Manager
      print("IDM User: %s\nIDM Password: %s\n" % (vals['web_gui_user'], vals['web_gui_pw']))

      return vals['idp_type']
