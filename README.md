###server side install python-openssl
    sudo aptitude install python-openssl

###use openssl to generate your key and cert file

    openssl genrsa -out privkey.pem 2048
    openssl req -new -x509 -key privkey.pem -out cacert.pem -days 1095

### other
    tested on ubuntu 11.10 x64  python2.7

###modified from http://xiaoxia.org/2011/03/29/written-by-python-socks5-server/ 

copyring by original author

