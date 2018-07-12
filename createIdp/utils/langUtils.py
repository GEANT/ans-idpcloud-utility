#!/usr/bin/env python
# coding=utf-8

from collections import OrderedDict

def get_os_orderedDict(lang):

   if (lang == 'it-IT'):
      return OrderedDict([
               ("ip_priv","Inserisci l'IP Privato della VM: "),
               ("ip_pub","Inserisci l'IP Pubblico della VM: "),
               ("boot_vlm_size","Inserisci la dimensione, in GB, del disco di boot della VM: (default: 10)"),
               ("boot_vlm_image","Inserisci la distribuzione che verrà installata sulla VM (default: Debian-8.8.2): "),
               ("flavor","Inserisci il flavor della VM (default: idem-idpcloud): "),
               ("data_vlm_size","Vuoi aggiungere un ulteriore volume persistente? (default: no): "),
               ("sec_groups","Aggiungere security groups aggiuntivi oltre a default? (default: no): "),
            ])

def get_yml_orderedDict(lang):

   if (lang == 'it-IT'):
      return OrderedDict([
               ("mdui_displayName_it","Inserisci il nome dell'istituzione in ITALIANO: "),
               ("mdui_displayName_en","Inserisci il nome dell'istituzione in INGLESE: "),
               ("domain","Inserisci il dominio dell'istituzione: "),
               ("org_url_it","Inserisci il sito istituzionale pubblico in ITALIANO: "),
               ("org_url_en","Inserisci il sito istituzionale pubblico in INGLESE: "),
               ("mdui_logo_it","Inserisci la URL HTTPS del Logo ITALIANO(160x120) dell'istituzione (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_logo_en","Inserisci la URL HTTPS del Logo INGLESE(160x120) dell'istituzione (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_favicon_it","Inserisci la URL HTTPS della Favicon ITALIANA (32x32) dell'istituzione (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_favicon_en","Inserisci la URL HTTPS della Favicon INGLESE (32x32) dell'istituzione (premi 'Invio' per tenere il valore predefinito): "),
               ("footer_bkgr_color","Inserisci il colore esadecimale rappresentativo dell'istituzione (premi 'Invio' per generare un valore casuale): "),
               ("mdui_description_it","Inserisci la descrizione dell'IdP istituzionale in lingua ITALIANA (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_description_en","Inserisci la descrizione dell'IdP istituzionale in lingua INGLESE (premi 'Invio' per tenere il valore predefinito ): "),
               ("mdui_privacy_it","Inserisci la pagina di Privacy Policy per l'IdP in ITALIANO (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_privacy_en","Inserisci la pagina di Privacy Policy per l'IdP in INGLESE (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_info_it","Inserisci la pagina Informativa per l'IdP in ITALIANO (premi 'Invio' per tenere il valore predefinito): "),
               ("mdui_info_en","Inserisci la pagina Informativa per l'IdP in INGLESE (premi 'Invio' per tenere il valore predefinito): "),
               ("idp_support_email","Inserisci la mail di supporto per gli utenti dell'IdP istituzionale (premi 'Invio' per tenere il valore 'idpcloud-service@garr.it'): "),
               ("idp_support_address","Inserisci l'indirizzo postale dell'istituzione (premi 'Invio' per inserire in futuro): "),
               ("idp_type","Inserisci 'Debian-IdP-with-IdM-GARR' o 'Debian-IdP-without-IdM': (premi 'Invio' per 'Debian-IdP-with-IdM-GARR'): "),
               ("ca","1) TERENA_SSL_CA_2\n2) TERENA_SSL_CA_3\n\nScegli 1 o 2 (o premi 'Invio' 'TERENA_SSL_CA_3'): "),
               ("idp_persistentId_salt","Inserisci il persistent-id salt da applicare (premi 'Invio' per generare un valore casuale): "),
               ("idp_fticks_salt","Inserisci il salt per gli f-ticks da applicare (premi 'Invio' per generare un valore casuale): "),
               ("web_gui_user","Inserisci il nome dell'utente che accederà via Web l'IDM dell'IdP (premi 'Invio' per tenere il valore predefinito 'idm-admin'): "),
               ("web_gui_pw","Inserisci la password dell'utente che accederà via web all'IDM dell'IdP (premi 'Invio' per generare un valore casuale): "),
               ("root_ldap_pw","Inserisci la password dell'utente 'admin' di openLDAP (premi 'Invio' per generare un valore casuale): "),
               ("mysql_root_password","Inserisci la password dell'utente 'root' di MySQL (premi 'Invio' per generare un valore casuale): "),
               ("shibboleth_db_password","Inserisci la password dell'utente 'shibboleth' di MySQL (premi 'Invio' per generare un valore casuale): "),
               ("bindDNCredential","Inserisci la password dell'utente 'idpuser' di OpenLDAP (premi 'Invio' per generare un valore casuale): "),
               ("idp_stats_db_pw","Inserisci la password dell'utente 'statistics' di MySQL (premi 'Invio' per generare un valore casuale): "),
               ("flup_secret_key","Inserisci la secret key di FLUP (premi 'Invio' per generare un valore casuale): "),
               ("idpcloud_idm","Inserisci 'spuid' per riconoscere gli utenti con il Codice Fiscale(schacPersonalUniqueID) o\nInserisci 'email' per riconoscere gli utenti con la loro e-mail personale (premi 'Invio' per 'spuid'): "),
            ])
