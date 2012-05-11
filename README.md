##a simple socks5 server,using ssl as tunnel

<del>server side install python-openssl</del>
<del>sudo aptitude install python-openssl</del>
<del>sudo pip install pyOpenSSL</del>

###on server,use openssl to generate your key and cert file

    openssl genrsa -out privkey.pem 2048
    openssl req -new -x509 -key privkey.pem -out cacert.pem -days 1095

###test
test
+ server:ubuntu 11.10 x64  python2.7
+ client:windows7 python 2.7.3,ubuntu 11.10 python 2.7.2

###todo
ipv6 support

###other
modified from <http://xiaoxia.org/2011/03/29/written-by-python-socks5-server/>
copyring by original author

