#!/usr/bin/env python
# coding=utf-8

import utils
import argparse
import os
import sys

# CONSTANTS

CSR_DEST = "/opt/idpcloud-data/ansible-shibboleth/roles/common/files"
YML_DEST = "/opt/idpcloud-data/ansible-shibboleth/inventories/production/host_vars"
YML_LNK_DIR ="/opt/ansible-shibboleth/inventories/production/host_vars"
PLA_DEST = "/opt/ansible-shibboleth/roles/phpldapadmin/files/restore"
ANS_SHIB_ROLES = "/opt/ansible-shibboleth/roles"

# END CONSTANTS

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-n", "--name", help="Provide the FQDN", action="store", default="")
   parser.add_argument("-f", "--force", help="Force regeneration YML file", action="store_true", default=False)
   parser.add_argument("-r", "--req_info", help="Set C,ST,L,O,OU? [y|n]", action="store", default="n")
   parser.add_argument("-s", "--san", help="SANS", action="store", nargs='*', default="")
   parser.add_argument("-c", "--csr", help="Generate SSL CSR and SSL Key Only", action="store_true", default=False)
   parser.add_argument("-y", "--yml", help="Generate IdP YML file Only", action="store_true", default=False)
   parser.add_argument("-o", "--os", help="Generate OS YML file Only", action="store_true", default=False)
   parser.add_argument("-e", "--everything", help="Generate SSL credentials, IdP and OS YML files", action="store_true", default=False)
   args = parser.parse_args()
  
   if(args.name and not(args.csr == args.yml == args.os == args.everything == args.test == False)):
    if(args.force):
     os.remove(YML_LNK_DIR+'/'+args.name+'.yml')
     os.remove(YML_DEST+'/'+args.name+'.yml')
     os.remove(PLA_DEST+'/'+args.name)
 
    if (args.csr):
     #Create CSR and KEY for the IdP
     utils.generate_csr(args.name, args.req_info, CSR_DEST, args.san)

    if (args.yml):
     # Create or Retrieve the Shibboleth IdP sealer/keystore password
     idp_sealer_pw = utils.get_sealer_keystore_pw(args.name,False)

     # Create the IdP YAML file
     utils.create_idp_yml(args.name,CSR_DEST+'/'+args.name,YML_DEST,idp_sealer_pw)

    if (args.os):
     # Add new IdP to the /opt/ansible-openstack/inventories/production/group_vars/openstack-client.yml
     utils.create_openstack_client_yml(args.name)

    # If I run script with only "--name" I have to follow all steps
    if (args.everything):
      # Create CSR and KEY for the IdP
      utils.generate_csr(args.name, args.req_info, CSR_DEST, args.san)

      # Create or Retrieve the Shibboleth IdP sealer/keystore password
      idp_sealer_pw = utils.get_sealer_keystore_pw(args.name,False)

      # Create the IdP YAML file
      utils.create_idp_yml(args.name,CSR_DEST+'/'+args.name,YML_DEST,idp_sealer_pw)

      # Add new IdP to the /opt/ansible-openstack/inventories/production/group_vars/openstack-client.yml
      utils.create_openstack_client_yml(args.name)

    os.system('ln -s %s/%s %s/common/files' % (CSR_DEST,args.name,ANS_SHIB_ROLES))
    os.system('cp -R %s/idp/files/restore/sample-FQDN-dir/styles/images/ %s/idp/files/restore/%s/styles' % (ANS_SHIB_ROLES,ANS_SHIB_ROLES,args.name))
    os.system('cp -R %s/idp/files/restore/sample-FQDN-dir/mysql-backup/ %s/idp/files/restore/%s' % (ANS_SHIB_ROLES,ANS_SHIB_ROLES,args.name))
   else:
      print("!!! FQDN(--name) o modalità di creazione mancante !!!\n")
      parser.print_help()
