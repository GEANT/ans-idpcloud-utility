#!/usr/bin/env python
# coding=utf-8

import utils
import argparse
import os
import sys
import shutil
import logging

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("fqdn", help="Full Qualified Domain Name of Shibboleth IdP")
   parser.add_argument("--entityid", help="Provide the entityID for the IdP", action="store", default="")
   parser.add_argument("--force", help="Force regeneration ansible-shibboleth YML file", action="store_true", default=False)
   parser.add_argument("--csr", help="Generate SSL CSR and SSL Key Only", action="store_true", default=False)
   parser.add_argument("--yml", help="Generate IdP YML file Only", action="store_true", default=False)
   parser.add_argument("--everything", help="Generate SSL credentials and IdP YML files", action="store_true", default=False)
   args = parser.parse_args()
 
   # CONSTANTS STARTS
   ANS_SHIB = "/opt/ansible-shibboleth"
   ANS_VAULT_FILE = "/opt/idpcloud-ansible-master/.vault_pass"
   ANS_SHIB_INV = ANS_SHIB + "/inventories"
   ANS_SHIB_INV_FILES = ANS_SHIB_INV + "/files"
   ANS_SHIB_INV_PROD = ANS_SHIB_INV + "/production"

   IDP_PROD_HOST_VARS = ANS_SHIB_INV_PROD + "/host_vars"
   IDP_YML = IDP_PROD_HOST_VARS + '/' + args.fqdn + '.yml'

   IDP_FILES_DIR = ANS_SHIB_INV_FILES+'/'+args.fqdn
   IDP_SAMPLE_FILES_DIR = ANS_SHIB_INV_FILES+'/sample-FQDN-dir'
   IDP_PLA_FILES_DIR = IDP_FILES_DIR + '/phpldapadmin'
   IDP_SSL_DIR = IDP_FILES_DIR + '/common/ssl'
   IDP_CRED_DIR = IDP_FILES_DIR + '/idp/credentials'
   IDP_STYLES_DIR = IDP_FILES_DIR + '/idp/styles'
   IDP_STYLES_DIR_SAMPLE = IDP_SAMPLE_FILES_DIR + '/idp/styles'
   # CONSTANTS END

   # Remove LOG file before start
   os.system("rm logs/createIdP.log")

   # Create a new LOG file
   logging.basicConfig(filename='logs/createIdP.log', format='%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.DEBUG)

   if(args.fqdn and (args.csr == True or args.yml == True or args.everything == True)):
    if(args.force):
     logging.debug("Removing '%s' files..." % (args.fqdn))
     os.system("sed -i '/"+args.fqdn+"/d' "+ ANS_SHIB_INV_PROD + "/production.ini")
     os.remove(IDP_YML)
     shutil.rmtree(IDP_FILES_DIR)
     logging.debug("...files deleted.")
 
    # If I run the script with "--fqdn" and "--csr"
    if (args.csr):
     logging.debug("Creating SSL CSR and KEY for '%s' ..." % (args.fqdn))
     #Create CSR and KEY for the IdP, if not exist, in IDP_SSL_DEST
     utils.generate_csr(args.fqdn, IDP_SSL_DIR)
     logging.debug("...SSL CSR and KEY created.")

    # If I run the script with "--fqdn" and "--yml"
    if (args.yml):
     logging.debug("Creating IdP credentials for '%s' ..." % (args.fqdn))
     # Create or Retrieve the Shibboleth IdP sealer/keystore password
     idp_sealer_pw = utils.get_sealer_keystore_pw(args.fqdn, args.entityid, IDP_CRED_DIR, ANS_VAULT_FILE, False)
     logging.debug("...IdP credentials created.")

     # Create the IdP YAML file and ecrypt it with Ansible Vault
     logging.debug("Creating IDP YAML file for '%s' ..." % (args.fqdn))
     utils.create_idp_yml(args.fqdn, args.entityid, IDP_SSL_DIR, IDP_YML, IDP_STYLES_DIR, IDP_PLA_FILES_DIR, idp_sealer_pw, ANS_VAULT_FILE)
     logging.debug("...IDP YAML file created.")

    # If I run script with "--fqdn" and "--everything" I have to follow all steps
    if (args.everything):
     logging.debug("Creating all needed files for '%s' IdP ..." % (args.fqdn))
     logging.debug("Creating SSL CSR and KEY ...")
     # Create CSR and KEY for the IdP, if not exist, in the IDP_SSL_DEST directory
     utils.generate_csr(args.fqdn, IDP_SSL_DIR)
     logging.debug("...SSL CSR and KEY created.")
 
     logging.debug("Creating IdP credentials ...")
     # Create or Retrieve the Shibboleth IdP sealer/keystore password
     idp_sealer_pw = utils.get_sealer_keystore_pw(args.fqdn, args.entityid, IDP_CRED_DIR, ANS_VAULT_FILE, False)
     logging.debug("...IdP credentials created.")

     logging.debug("Creating IDP YAML file ...")
     # Create the IdP YAML file
     idp_type = utils.create_idp_yml(args.fqdn, args.entityid, IDP_SSL_DIR, IDP_YML, IDP_FILES_DIR + '/idp/styles', IDP_FILES_DIR + '/phpldapadmin', idp_sealer_pw, ANS_VAULT_FILE)
     logging.debug("...IDP YAML file created.")

     # Add the new IdP on the production.ini file
     logging.debug("Adding the IDP to 'production' inventory...")
     utils.add_idp_to_inventory(args.fqdn, idp_type, ANS_SHIB_INV_PROD + '/production.ini')
     logging.debug("...IDP added to 'production' inventory.")

     # Copy italian and english flags on the IdP styles dir
     logging.debug("Copying samples flags into the IdP directory...")
     os.system('cp -nr %s/idp/styles/it/itFlag.png %s/idp/styles/it/itFlag.png' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
     os.system('cp -nr %s/idp/styles/en/enFlag.png %s/idp/styles/en/enFlag.png' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
     logging.debug("...samples flags copied.")

     # Copy federation and interfederation logo on the IdP styles dir
     logging.debug("Copying federation and interfederation logos into the IdP directory...")
     os.system('cp -nr %s/idp/styles/images %s/idp/styles' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
     logging.debug("...federation and interfederation logos copied.")

     # Create 'idp/mysql-restore' dir with its README.md file
     logging.debug("Copying MySQL restore directory into the IDP directory...")
     os.system('cp -nr %s/idp/mysql-restore %s/idp' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
     logging.debug("...MySQL restore directory copied.")

     # Create 'idp/conf' dir with its content
     logging.debug("Copying IdP 'conf' directory into the IDP directory...")
     os.system('cp -nr %s/idp/conf %s/idp' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
     logging.debug("...IdP 'conf' directory copied.")
      
     # Create 'openldap' dir with its content
     logging.debug("Copying IdP OpenLDAP restore directory into the IDP directory...")
     os.system('cp -nr %s/openldap %s' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
     logging.debug("...IdP OpenLDAP restore directory copied.")

   else:
      print("!!! FQDN(--fqdn) or generation's mode missing !!!\n")
      parser.print_help()
