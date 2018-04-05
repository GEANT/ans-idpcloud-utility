#!/usr/bin/env python
# coding=utf-8

import os
from collections import OrderedDict
from subprocess import check_output,call
from jinja2 import Environment, FileSystemLoader

### FUNCTIONS TO CREATE IDP YAML FILE ###

def prepare(vals):
   # Create the jinja2 environment.
   # Notice the use of trim_blocks, which greatly helps control whitespace.
   j2_env = Environment(loader=FileSystemLoader(os.getcwd()),keep_trailing_newline=True,trim_blocks=True,lstrip_blocks=True)
   result = j2_env.get_template('templates/openstack-client.yml.j2').render(j2_vals=vals)
   return result

def create_openstack_client_yml(idp_fqdn, os_client_dest):

   if(idp_fqdn in open(os_client_dest).read()):
      print("\nOpenstack Client YAML file is already configured for your '%s' IDP." % idp_fqdn)
   else:
      question_dict = OrderedDict([
         ("ip_priv","Inserisci l'IP Privato della VM: "),
         ("ip_pub","Inserisci l'IP Pubblico della VM: "),
         ("boot_vlm_size","Inserisci la dimensione, in GB, del disco di boot della VM: (default: 10)"),
         ("boot_vlm_image","Inserisci la distribuzione che verrà installata sulla VM (default: Debian-8.8.2): "),
         ("flavor","Inserisci il flavor della VM (default: idem-idpcloud): "),
         ("data_vlm_size","Vuoi aggiungere un ulteriore volume persistente? (default: no): "),
         ("sec_groups","Aggiungere security groups aggiuntivi oltre a default? (default: no): "),
      ])

      vals = {}

      vals['fqdn'] = idp_fqdn

      for key,question in question_dict.iteritems():

         result = ""

         while (result == "" or result == None):
            result = raw_input(question)

            if ( key == 'boot_vlm_image' and (result == "" or result == None) ):
               result = 'Debian-8.8.2'
            if ( key == 'boot_vlm_size' and (result == "" or result == None) ):
               result = '10'
            elif ( key == 'flavor' and (result == "" or result == None) ):
               result = 'idem-idpcloud'
            elif ( key == 'data_vlm_size' and (result == 'yes' or result == 'y' or result == 'si' or result == 's') or result == 'sì'):
               result = raw_input("Inserisci la dimensione, in GB, del disco dati della VM: ")
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

                  answer = raw_input("Inserire un altro security group? (y|n): ")

            elif ( key == 'sec_groups' and (result == '' or result == None) ):
               result = {}
               result[0] = 'default'

         vals[key] = result

      os_client_yml = open(os_client_dest, "a+")
      values = prepare(vals)
      os_client_yml.write(values)
      os_client_yml.close()
