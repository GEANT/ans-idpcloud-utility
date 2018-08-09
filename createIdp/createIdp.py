#!/usr/bin/env python
# coding=utf-8

import utils
import argparse
import os
import sys
import shutil

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("--fqdn", help="Provide the FQDN", action="store", default="", required=True)
   parser.add_argument("--entityID", help="Provide the entityID for the IdP", action="store", default="")
   parser.add_argument("--force", help="Force regeneration ansible-shibboleth YML file", action="store_true", default=False)
   parser.add_argument("--csr", help="Generate SSL CSR and SSL Key Only", action="store_true", default=False)
   parser.add_argument("--yml", help="Generate IdP YML file Only", action="store_true", default=False)
   parser.add_argument("--everything", help="Generate SSL credentials, IdP and OS YML files", action="store_true", default=False)
   args = parser.parse_args()
 
   # CONSTANTS STARTS
   ANS_SHIB = "/opt/ansible-shibboleth"
   ANS_VAULT_FILE = "/opt/idpcloud-ansible-master/.vault_pass"
   ANS_SHIB_INV = ANS_SHIB + "/inventories"
   ANS_SHIB_INV_FILES = ANS_SHIB_INV + "/files"
   ANS_SHIB_INV_PROD = ANS_SHIB_INV + "/production"

   IDP_YML_HOST_VARS = ANS_SHIB_INV_PROD + "/host_vars"
   IDP_YML = IDP_YML_HOST_VARS + '/' + args.fqdn + '.yml'

   IDP_FILES_DIR = ANS_SHIB_INV_FILES+'/'+args.fqdn
   IDP_SAMPLE_FILES_DIR = ANS_SHIB_INV_FILES+'/sample-FQDN-dir'
   IDP_PLA_FILES_DIR = IDP_FILES_DIR + '/phpldapadmin'
   IDP_SSL_DIR = IDP_FILES_DIR + '/common/ssl'
   IDP_CRED_DIR = IDP_FILES_DIR + '/idp/credentials'
   IDP_STYLES_DIR = IDP_FILES_DIR + '/idp/styles'
   IDP_STYLES_DIR_SAMPLE = IDP_SAMPLE_FILES_DIR + '/idp/styles'

   # CONSTANTS END

   if(args.fqdn and not(args.csr == args.yml == args.os == args.everything == False)):
    if(args.force):
     os.remove(IDP_YML)
     shutil.rmtree(IDP_FILES_DIR)
 
    # If I run the script with "--fqdn" and "--csr"
    if (args.csr):
     #Create CSR and KEY for the IdP, if not exist, in IDP_SSL_DEST
     utils.generate_csr(args.fqdn, args.req_info, IDP_SSL_DIR, args.san)

    # If I run the script with "--fqdn" and "--yml"
    if (args.yml):
     # Create or Retrieve the Shibboleth IdP sealer/keystore password
     idp_sealer_pw = utils.get_sealer_keystore_pw(args.fqdn, args.entityID, IDP_CRED_DIR, ANS_VAULT_FILE, False)

     # Create the IdP YAML file and ecrypt it with Ansible Vault
     utils.create_idp_yml(args.fqdn, args.entityID, IDP_SSL_DIR, IDP_YML, IDP_STYLES_DIR, IDP_PLA_FILES_DIR, idp_sealer_pw, ANS_VAULT_FILE)

    # If I run script with "--fqdn" and "--everything" I have to follow all steps
    if (args.everything):
      # Create CSR and KEY for the IdP, if not exist, in the IDP_SSL_DEST directory
      utils.generate_csr(args.fqdn, args.req_info, IDP_SSL_DIR, args.san)
 
      # Create or Retrieve the Shibboleth IdP sealer/keystore password
      idp_sealer_pw = utils.get_sealer_keystore_pw(args.fqdn, args.entityID, IDP_CRED_DIR, ANS_VAULT_FILE, False)

      # Create the IdP YAML file
      idp_type = utils.create_idp_yml(args.fqdn, args.entityID, IDP_SSL_DIR, IDP_YML, IDP_FILES_DIR + '/idp/styles', IDP_FILES_DIR + '/phpldapadmin', idp_sealer_pw, ANS_VAULT_FILE)

      # Add the new IdP on the production.ini file
      utils.add_idp_to_inventory(args.fqdn, idp_type, ANS_SHIB_INV_PROD + '/production.ini')

      # Copy italian and english flags on the IdP styles dir
      os.system('cp -nr %s/idp/styles/it/itFlag.png %s/idp/styles/it/itFlag.png' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
      os.system('cp -nr %s/idp/styles/en/enFlag.png %s/idp/styles/en/enFlag.png' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))

      # Copy federation and interfederation logo on the IdP styles dir
      os.system('cp -nr %s/idp/styles/images %s/idp/styles/images' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))

      # Create 'idp/mysql-restore' dir with its README.md file
      os.system('cp -nr %s/idp/mysql-restore %s/idp/mysql-restore' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))

      # Create 'idp/conf' dir with its content
      os.system('cp -nr %s/idp/conf %s/idp/conf' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))
      
      # Create 'openldap' dir with its content
      os.system('cp -nr %s/openldap %s/openldap' % (IDP_SAMPLE_FILES_DIR, IDP_FILES_DIR))

   else:
      print("!!! FQDN(--fqdn) or generation's mode missing !!!\n")
      parser.print_help()
