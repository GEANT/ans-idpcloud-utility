# createSSLcredentials.sh - HOWTO Create your own CA, SSL Key and SSL Certificates for testing

This repository contains useful instructions that allow to create SSL Certificate and SSL Keys for testing ansible-shibboleth recipes

## Requirements
* `apt-get install openssl`

## Instructions

1. Create needed directories:

   * `sudo mkdir -p /etc/ssl/CA/certs /etc/ssl/CA/crl /etc/ssl/CA/newcerts /etc/ssl/CA/private`
   * `sudo chmod 700 /etc/ssl/CA/private`

2. Generate the SSL CA Key:
   * `openssl genrsa -aes256 -out /etc/ssl/CA/private/myCA.key 4096`
   * `chmod 400 /etc/ssl/CA/private/myCA.key`

3. Save the original 'openssl.conf' file:
   * `cp /etc/ssl/openssl.cnf /etc/ssl/openssl.cnf.orig`

4. Modify 'openssl.conf' as follows:
   * `vim /etc/ssl/openssl.cnf`

     ```
     [ CA_default ]

     dir = /etc/ssl/CA     # Where everything is kept
     ...
     certificate 	= $dir/certs/myCA.crt  	# The CA certificate
     private_key 	= $dir/private/myCA.key # The CA private key

     ...
     policy = policy_anything

     req_extensions = v3_req

     [ req_distinguished_name ]
     countryName			            = Country Name (2 letter code)
     countryName_default		      = IT
     countryName_min			         = 2
     countryName_max			         = 2

     stateOrProvinceName		      = State or Province Name (full name)
     stateOrProvinceName_default	   = Italy

     localityName			            = Locality Name (eg, city)
     localityName_default		      = Rome

     0.organizationName		         = Organization Name (eg, company)
     0.organizationName_defaul	   = Example Organization

     organizationalUnitName		   = Organizational Unit Name (eg, section)
     organizationalUnitName_default	= Example

     commonName			            = Common Name (e.g. server FQDN or YOUR name)
     commonName_default		         = Example CA
     commonName_max			         = 64

     emailAddress			            = Email Address
     emailAddress_default		      = custom-ca@example.org
     emailAddress_max		         = 64

     [ usr_cert ]

     keyUsage = nonRepudiation, digitalSignature, keyEncipherment

     ...

     [ v3_req ]

     # Extensions to add to a certificate request

     basicConstraints = CA:FALSE
     keyUsage = nonRepudiation, digitalSignature, keyEncipherment
     subjectAltName = @alt_names

     # Example shows how to support ALL 'example.org' servers
     [ alt_names ]
     DNS.1 = *.example.org

     [ v3_ca ]
     ...
     keyUsage = cRLSign, keyCertSign

     # Some might want this also
     nsCertType = sslCA
     ```

5. Generate the CA Certificate (10950 == 30 years):
   * ```openssl req -new -x509 -days 10950 -key /etc/ssl/CA/private/myCA.key -extensions v3_ca -out /etc/ssl/CA/certs/myCA.crt -config /etc/ssl/openssl.cnf```

6. Create your 'ssl-generator.sh' script:
   * ```vim /etc/ssl/CA/ssl-generator.sh```

     ```
     #!/bin/bash

     read -p "Insert the machine HOSTNAME [es: cerbero]: " HOSTNAME

       if [[ "${HOSTNAME}" =~ '^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]' ]]; then
         echo "ERROR: hostname not valid!"
         exit 1
       fi


     read -p "Insert the machine DOMAIN [es: example.org]: " DOMAIN_NAME

       if [[ "${DOMAIN_NAME}" =~ '^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[it|com|net|org]' ]]; then
         echo "ERRORE: domain not valid!"
         exit 1
       fi

     cd /etc/ssl/CA

     echo "Generating the KEY for ${HOSTNAME}.${DOMAIN_NAME}:"
     openssl genrsa -out private/${HOSTNAME}.${DOMAIN_NAME}.key 4096
     chmod 400 private/${HOSTNAME}.${DOMAIN_NAME}.key

     echo "Generating the CSR for ${HOSTNAME}.${DOMAIN_NAME}:"
     openssl req -new -sha512 -extensions v3_req -key private/${HOSTNAME}.${DOMAIN_NAME}.key -out certs/${HOSTNAME}.${DOMAIN_NAME}.csr -subj "/CN=${HOSTNAME}.${DOMAIN_NAME}"

     echo "Generating the CRT for ${HOSTNAME}.${DOMAIN_NAME} (SHA512 & 30 years valid):"
     openssl x509 -req -extensions v3_req -days 10950 -sha512 -in certs/${HOSTNAME}.${DOMAIN_NAME}.csr -CA /etc/ssl/CA/certs/myCA.crt -CAkey /etc/ssl/CA/private/myCA.key -CAcreateserial -out certs/${HOSTNAME}.${DOMAIN_NAME}.crt -extfile /etc/ssl/openssl.cnf

     echo "Verifying CRT generated:"
     openssl verify -CAfile certs/myCA.crt certs/${HOSTNAME}.${DOMAIN_NAME}.crt

     echo ""
     echo "To send the certificate into the '/tmp' directory of the VM \"${HOSTNAME}.${DOMAIN_NAME}\" run these commands:"
     echo ""
     echo "scp /etc/ssl/CA/certs/myCA.crt <USERNAME>@${HOSTNAME}.${DOMAIN_NAME}:/tmp"
     echo ""
     echo "scp /etc/ssl/CA/certs/${HOSTNAME}.${DOMAIN_NAME}.crt <USERNAME>@${HOSTNAME}.${DOMAIN_NAME}:/tmp"
     echo ""
     echo "scp /etc/ssl/CA/private/${HOSTNAME}.${DOMAIN_NAME}.key <USERNAME>@${HOSTNAME}.${DOMAIN_NAME}:/tmp"
     echo ""
     echo "Remember to:"
     echo "1) Copy the CA certificate into '/usr/local/share/ca-certificates/myCA.crt' of the destination host and run 'update-ca-certificates'"
     echo ""
     echo "2) Copy the SSL Certificate and the SSL Key on the destination host:"
     echo "   cp /tmp/${HOSTNAME}.${DOMAIN_NAME}.crt /etc/ssl/certs"
     echo "   cp /tmp/${HOSTNAME}.${DOMAIN_NAME}.key /etc/ssl/private"
     echo "   cp /tmp/myCA.crt /usr/local/share/ca-certificates/myCA.crt"
     echo "   update-ca-certificates"
     echo ""
     echo "3) Import your own CA, found into /etc/ssl/CA/certs/myCA.crt, on your web browsers."
     echo ""
     ```
7. Generate new SSL Certs and Keys with:
   * ```/bin/bash /etc/ssl/CA/ssl-generator.sh```

### Authors

#### Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
