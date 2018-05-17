#!/usr/bin/env python
# coding=utf-8

import utils
import argparse
import os
import sys

# CONSTANTS

ANS_SHIB = "/opt/ansible-shibboleth"
ANS_SHIB_INV = ANS_SHIB + "/inventories"
ANS_SHIB_ROLES = ANS_SHIB + "/roles"

IDP_YML_LNK_DEST = ANS_SHIB_INV + "/production/host_vars"
CSR_DEST = ANS_SHIB_ROLES + "/common/files"
PLA_DEST = ANS_SHIB_ROLES + "/phpldapadmin/files/restore"

DATA = "/opt/idpcloud-data"
DATA_ANS_SHIB = DATA + "/ansible-shibboleth"
DATA_ANS_SHIB_INV = DATA_ANS_SHIB + "/inventories"
DATA_ANS_SHIB_ROLES = DATA_ANS_SHIB + "/roles"
DATA_ANS_VAULT_FILE = DATA + "/.vault_pass"

IDP_YML_DEST = DATA_ANS_SHIB_INV + "/production/host_vars"
CSR_DEST_DATA = DATA_ANS_SHIB_ROLES + "/common/files"

OS_CLIENT_DEST= DATA + "/ansible-openstack/inventories/production/group_vars/openstack-client.yml"

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
     os.remove(IDP_YML_LNK_DEST+'/'+args.name+'.yml')
     os.remove(IDP_YML_DEST+'/'+args.name+'.yml')
     os.remove(PLA_DEST+'/'+args.name)
 
    if (args.csr):
     #Create CSR and KEY for the IdP
     utils.generate_csr(args.name, args.req_info, CSR_DEST_DATA, args.san)

    if (args.yml):
     # Create or Retrieve the Shibboleth IdP sealer/keystore password
     idp_sealer_pw = utils.get_sealer_keystore_pw(args.name, DATA_ANS_SHIB, DATA_ANS_VAULT_FILE, False)

     # Create the IdP YAML file
     utils.create_idp_yml(args.name,CSR_DEST_DATA+'/'+args.name,IDP_YML_DEST, DATA_ANS_SHIB, ANS_SHIB, idp_sealer_pw)

     ans_shib_idp_yml_lnk = ANS_SHIB + "/inventories/production/host_vars/"+ args.name + ".yml"

     if (os.path.islink(ans_shib_idp_yml_lnk)):
        print ("IDP YAML already linked: %s" % ans_shib_idp_yml_lnk)
     else:
        print ("CREO LINK IN ANSIBLE-SHIBBOLETH")
        os.system('ln -s %s.yml %s.yml' % (DATA_ANS_SHIB +"/inventories/production/host_vars/"+ args.name, ANS_SHIB +"/inventories/production/host_vars/"+ args.name))
    if (args.os):
     # Add new IdP to the /opt/ansible-openstack/inventories/production/group_vars/openstack-client.yml
     utils.create_openstack_client_yml(args.name, OS_CLIENT_DEST)

    # If I run script with only "--name" I have to follow all steps
    if (args.everything):
      # Create CSR and KEY for the IdP in the DATA directory
      utils.generate_csr(args.name, args.req_info, CSR_DEST_DATA, args.san)
 
      # Create link on the ansible-shibboleth main dir
      ans_shib_idp_https_cred_lnk = CSR_DEST +"/"+ args.name

      if (os.path.islink(ans_shib_idp_https_cred_lnk)):
         print ("IDP HTTPS Credentials directory already linked: %s" % ans_shib_idp_https_cred_lnk)
      else:
         os.system('ln -s %s/%s %s/%s' % (CSR_DEST_DATA, args.name, CSR_DEST, args.name))

      # Create or Retrieve the Shibboleth IdP sealer/keystore password
      idp_sealer_pw = utils.get_sealer_keystore_pw(args.name, DATA_ANS_SHIB, DATA_ANS_VAULT_FILE, False)

      # Create link on the ansible-shibboleth/roles/idp/restore dir
      ans_shib_idp_restore_lnk = ANS_SHIB + "/roles/idp/files/restore"+ args.name

      if (os.path.islink(ans_shib_idp_restore_lnk)):
         print ("IDP restore directory already linked: %s" % ans_shib_idp_restore_lnk)
      else:
         os.system('ln -s %s/%s %s/%s' % (DATA_ANS_SHIB + "/roles/idp/files/restore", args.name, ANS_SHIB + "/roles/idp/files/restore", args.name))

      # Create the IdP YAML file
      utils.create_idp_yml(args.name,CSR_DEST_DATA+'/'+args.name,IDP_YML_DEST, DATA_ANS_SHIB, ANS_SHIB, idp_sealer_pw)

      ans_shib_pla_idp_dir_lnk = ANS_SHIB +"/roles/phpldapadmin/files/restore/"+ args.name
      ans_shib_idp_yml_lnk = ANS_SHIB + "/inventories/production/host_vars/"+ args.name + ".yml"
 
      if (os.path.islink(ans_shib_pla_idp_dir_lnk)):
         print ("phpLDAPadmin IDP directory already linked: %s" % ans_shib_pla_idp_dir_lnk)
      else:
         os.system('ln -s %s/%s %s/%s' % (DATA_ANS_SHIB + '/roles/phpldapadmin/files/restore', args.name, ANS_SHIB + "/roles/phpldapadmin/files/restore", args.name))

      if (os.path.islink(ans_shib_idp_yml_lnk)):
         print ("IDP YAML already linked: %s" % ans_shib_idp_yml_lnk)
      else:
         print ("CREO LINK IN ANSIBLE-SHIBBOLETH")
         os.system('ln -s %s.yml %s.yml' % (DATA_ANS_SHIB +"/inventories/production/host_vars/"+ args.name, ANS_SHIB +"/inventories/production/host_vars/"+ args.name))

      # Add new IdP to the /opt/ansible-openstack/inventories/production/group_vars/openstack-client.yml
      utils.create_openstack_client_yml(args.name, OS_CLIENT_DEST)

      # Copy italian and english flags on the new IdP dir
      os.system('cp -nr %s/idp/files/restore/sample-FQDN-dir/* %s/idp/files/restore/%s' % (ANS_SHIB_ROLES,DATA_ANS_SHIB_ROLES,args.name))
   else:
      print("!!! FQDN(--name) or other is missing!!!\n")
      parser.print_help()
