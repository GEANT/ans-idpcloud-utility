#!/usr/bin/env python
# coding=utf-8

import os
from subprocess import check_output,call
from jinja2 import Environment, FileSystemLoader
import utils

### FUNCTIONS TO CREATE IDP YAML FILE ###

def prepare(vals):
   # Create the jinja2 environment.
   # Notice the use of trim_blocks, which greatly helps control whitespace.
   j2_env = Environment(loader=FileSystemLoader(os.getcwd()),keep_trailing_newline=True,trim_blocks=True,lstrip_blocks=True)
   result = j2_env.get_template('templates/openstack-client.yml.j2').render(j2_vals=vals)
   return result

def create_openstack_client_yml(idp_fqdn, os_client_dest_prod, os_client_dest_dev):

   if(idp_fqdn in open(os_client_dest_prod).read()):
      print("\nYour IdP '%s' is already loaded on the Production 'openstack-client.yml' file." % idp_fqdn)
      
      if(idp_fqdn in open(os_client_dest_dev).read()):
         print("\nYour IdP '%s' is already loaded on the Development 'openstack-client.yml' file." % idp_fqdn)
   else:
      question_dict = utils.get_os_orderedDict('it-IT')

      vals = {}

      vals['fqdn'] = idp_fqdn

      for key,question in question_dict.iteritems():

         result = ""

         while (result == "" or result == None):
            result = raw_input(question)

            if ( key == 'boot_vlm_image' and (result == "" or result == None) ):
               result = 'Debian-8.10.10'
            if ( key == 'boot_vlm_size' and (result == "" or result == None) ):
               result = '10'
            elif ( key == 'flavor' and (result == "" or result == None) ):
               result = 'idem-idpcloud'
            elif ( key == 'data_vlm_size' and (result == 'yes' or result == 'y' or result == 'si' or result == 's') or result == 'sì'):
               result = raw_input("Insert the data disk size, in GB, for the VM: ")
            elif ( key == 'data_vlm_size' and (result == "" or result == None) ):
               result = 'no'
            elif ( key == 'sec_groups' and (result == 'yes' or result == 'y' or result == 'si' or result == 's' or result == 'sì') ):
               result = {}
               result[0] = 'default'

               answer = 'yes'            

               sec_grp_cnt = 1
               while (answer != "n"):
      
                  if ( answer == "y" or answer == "yes"):
                     qst = "SECURITY GROUP #"+ str(sec_grp_cnt) +": "
                     result[sec_grp_cnt] = raw_input(qst)
                     sec_grp_cnt = sec_grp_cnt + 1

                  answer = raw_input("Do you want to insert another security group? (y|n): ")

            elif ( key == 'sec_groups' and (result == '' or result == None) ):
               result = {}
               result[0] = 'default'

         vals[key] = result

      os_client_yml = open(os_client_dest_prod, "a+")
      values = prepare(vals)
      os_client_yml.write(values)
      os_client_yml.close()

      os_client_yml = open(os_client_dest_dev, "a+")
      values = prepare(vals)
      os_client_yml.write(values)
      os_client_yml.close()
