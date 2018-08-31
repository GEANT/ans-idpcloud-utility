#!/usr/bin/env python
#-*- coding: utf-8 -*-

### Function needed to manage Inventory files ###

def add_idp_to_inventory(idp_fqdn, idp_type, inventory_ini_file):
   from ConfigParser import SafeConfigParser
   
   parser = SafeConfigParser(allow_no_value=True)
   parser.read(inventory_ini_file)
   parser.set(idp_type, idp_fqdn)

   inv_file = open(inventory_ini_file,"w")
   parser.write(inv_file)

def del_idp_to_inventory(idp_fqdn, idp_type, inventory_ini_file):
   from ConfigParser import SafeConfigParser
   
   parser = SafeConfigParser(allow_no_value=True)
   parser.read(inventory_ini_file)
   parser.remove_option(idp_type, idp_fqdn)

   inv_file = open(inventory_ini_file,"w")
   parser.write(inv_file)
