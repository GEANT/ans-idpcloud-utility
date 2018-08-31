#!/usr/bin/env python
#-*- coding: utf-8 -*-

from operator import itemgetter
import sys, getopt
import argparse
from subprocess import check_output, call
import shlex
import os
from cStringIO import StringIO
import logging

# PARAMETERS

os.environ["JAVA_HOME"] = "/usr/lib/jvm/default-java/jre"

# END PARAMETERS

### FUNCTION NEEDED TO CREATE IDP METADATA CREDENTIALS

def get_sealer_keystore_pw(idp_fqdn, idp_entityID, dest, ans_vault_file, debug):

   if(idp_entityID):
      entityID = idp_entityID
   else:
      entityID = "https://" + idp_fqdn + "/idp/shibboleth"

   ### Create a password long 27 characters
   idp_cred_pw = check_output(shlex.split("openssl rand -base64 27")).strip()

   if(debug):
      logging.debug("IdP Credentials password : %s" % idp_cred_pw)

   ### Create IDP Credentials DIR
   credentials_dir = dest
   call(["mkdir", "-p", credentials_dir])

   if(debug):
      logging.debug("IdP 'credentials' directory created in: %s" % credentials_dir)

   ### Find the IDP /bin directory
   idp_bin_dir = check_output(shlex.split('find / -path "*shibboleth-identity-provider-*/bin"')).strip()

   if (debug):
      logging.debug("IdP 'bin' directory found in: %s" % idp_bin_dir)

   ### Generate Sealer JKS and KVER

   ## Check the existance of Sealer JKS and KVER
   sealer_jks = check_output(shlex.split('find '+credentials_dir+' -name "sealer.jks"')).strip()
   sealer_kver = check_output(shlex.split('find '+credentials_dir+' -name "sealer.kver"')).strip()

   if (not sealer_jks and not sealer_kver):
      call(["./seckeygen.sh", "--alias", "secret", "--storefile", credentials_dir + "/sealer.jks", "--storepass", idp_cred_pw, "--versionfile", credentials_dir + "/sealer.kver"], cwd=idp_bin_dir)
      ## Encrypt KEY with Ansible Vault
      # Needed to avoid output of 'call' commands
      FNULL = open(os.devnull, 'w')
      call(["ansible-vault", "encrypt", "sealer.jks", "--vault-password-file", ans_vault_file], cwd=credentials_dir, stdout=FNULL)
      FNULL.close()
   else:
      if (debug):
         logging.debug("IdP Sealer JKS created into: %s" % sealer_jks)
         logging.debug("IdP Sealer KVER created into: %s" % sealer_kver)

   ## Generate IDP Backchannel Certificate

   ## Check the existance of IDP Backchannell P12 and CRT
   backchannel_p12 = check_output(shlex.split('find '+credentials_dir+' -name "idp-backchannel.p12"')).strip()
   backchannel_crt = check_output(shlex.split('find '+credentials_dir+' -name "idp-backchannel.crt"')).strip()

   if (not backchannel_p12 and not backchannel_crt):
      call(["./keygen.sh", "--storefile", credentials_dir + "/idp-backchannel.p12", "--storepass", idp_cred_pw, "--hostname", idp_fqdn, "--lifetime", "30", "--uriAltName", entityID, "--certfile", credentials_dir + "/idp-backchannel.crt"], cwd=idp_bin_dir)
      ## Encrypt KEY with Ansible Vault
      # Needed to avoid output of 'call' commands
      FNULL = open(os.devnull, 'w')
      call(["ansible-vault", "encrypt", "idp-backchannel.p12", "--vault-password-file", ans_vault_file], cwd=credentials_dir, stdout=FNULL)
      FNULL.close()
   else:
      if (debug):
         logging.debug("IdP Backchannel PCKS12 created into: %s" % backchannel_p12)
         logging.debug("IdP Backchannel Certificate created into: %s" % backchannel_crt)

   ### Generate IDP Signing Certificate and Key

   ## Check the existance of Signing CRT and KEY
   signing_crt = check_output(shlex.split('find '+credentials_dir+' -name "idp-signing.crt"')).strip()
   signing_key = check_output(shlex.split('find '+credentials_dir+' -name "idp-signing.key"')).strip()

   if (not signing_crt and not signing_key):
      call(["./keygen.sh", "--hostname", idp_fqdn, "--lifetime", "30", "--uriAltName", entityID, "--certfile", credentials_dir + "/idp-signing.crt", "--keyfile", credentials_dir + "/idp-signing.key"], cwd=idp_bin_dir)
      ## Encrypt KEY with Ansible Vault
      # Needed to avoid output of 'call' commands
      FNULL = open(os.devnull, 'w')
      call(["ansible-vault", "encrypt", "idp-signing.key", "--vault-password-file", ans_vault_file], cwd=credentials_dir, stdout=FNULL)
      FNULL.close()
   else:
      if (debug):
         logging.debug("IdP Signing Certificate created into: %s" % signing_crt)
         logging.debug("IdP Signing Key created into: %s" % signing_key)

   ### Generate IDP Encryption Certificate and Key

   ## Check the existance of Encryption CRT and KEY
   encryption_crt = check_output(shlex.split('find '+credentials_dir+' -name "idp-encryption.crt"')).strip()
   encryption_key = check_output(shlex.split('find '+credentials_dir+' -name "idp-encryption.key"')).strip()

   if (not encryption_crt and not encryption_key):
      call(["./keygen.sh", "--hostname", idp_fqdn, "--lifetime", "30", "--uriAltName", entityID, "--certfile", credentials_dir + "/idp-encryption.crt", "--keyfile", credentials_dir + "/idp-encryption.key"], cwd=idp_bin_dir)
      ## Encrypt KEY with Ansible Vault
      # Needed to avoid output of 'call' commands
      FNULL = open(os.devnull, 'w')
      call(["ansible-vault", "encrypt", "idp-encryption.key", "--vault-password-file", ans_vault_file], cwd=credentials_dir, stdout=FNULL)
      FNULL.close()
   else:
      if (debug):
         logging.debug("IdP Encryption Certificate created into: %s" % encryption_crt)
         logging.debug("IdP Encryption Key created into: %s" % encryption_key)

   ### Generate a file containing the Credentials Password encrypted with Ansible Vault to be able to upload it on a private GIT

   if (not sealer_jks and not sealer_kver) and (not backchannel_p12 and not backchannel_crt) and (not signing_crt and not signing_key) and (not encryption_crt and not encryption_key):
      idp_cred_pw_file = open(credentials_dir+"/"+idp_fqdn+"_pw.txt","w")
      idp_cred_pw_file.write(idp_cred_pw)
      idp_cred_pw_file.close()

      # Needed to avoid output of 'call' commands
      FNULL = open(os.devnull, 'w')
      call(["ansible-vault", "encrypt", credentials_dir+"/"+idp_fqdn+"_pw.txt", "--vault-password-file", ans_vault_file], cwd=credentials_dir, stdout=FNULL)
      FNULL.close()
      return idp_cred_pw

   else:
      idp_cred_pw_file = open(credentials_dir+"/"+idp_fqdn+"_pw.txt","r")
      idp_cred_pw = idp_cred_pw_file.read()
      idp_cred_pw_file.close()
      if "ANSIBLE_VAULT" in idp_cred_pw:
         idp_cred_pw = check_output(shlex.split('ansible-vault view --vault-password-file '+ ans_vault_file+' '+ credentials_dir+'/'+idp_fqdn+'_pw.txt')).strip()
         return idp_cred_pw

      return idp_cred_pw
