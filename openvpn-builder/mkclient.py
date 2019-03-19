#!/usr/bin/env python3
import sys,os,shutil,subprocess,random, argparse
from shutil import copyfile
from random import randrange
from mkpasswd import pwlist
'''
Generate clients with cert and password authentication 
Script takes one arugement being a text file with 3 variables delimited by commas(,)
EX: matt,young,matty01@example.com
Uses easyrsa to create a client.ovpn config with a cert and randomly generated password, using a list from mkpasswd.py 
Information about client is stored in /etc/openvpn/vpn_clients/
'''
userdata = ' '
removedata = ' ' 

def check_client():
    os.system('tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep V | cut -d "/" -f2 | wc -l > /etc/openvpn/easy-rsa/pki/outindex.txt')
    f = open('/etc/openvpn/easy-rsa/pki/outindex.txt', 'r')
    number_of_clients = int(f.read())
    f.close()
    # Checks if any clients even exist
    if number_of_clients == 0:
        print("No clients ")
    else:
    # Displays number of clients and their names
        print("Number of clients: %d\n" % number_of_clients)
        os.system('tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d "=" -f 2 > /etc/openvpn/rc-names.txt' )
        f = open('/etc/openvpn/rc-names.txt', 'r')
        list_clients = (f.read())
        f.close()
        print('Name of clients on vpn server:\n%s' % list_clients)

def revoke_client():
    for client in removedata:
        print (client)
        os.chdir('/etc/openvpn/easy-rsa')
        # easyrsa function that revokes client cert
        os.system('tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d "=" -f 2 > /etc/openvpn/rc-names.txt' )
        f = open('/etc/openvpn/rc-names.txt', 'r')
        list_clients = (f.read())
        f.close()
        if client in list_clients:
            os.system('./easyrsa --batch revoke "%s"' % client)
            os.system('EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl')
            print('remove req')
            os.system('rm -f "pki/reqs/%s.req"' % client)
            print('remove private')
            os.system('rm -f "pki/private/%s.key"' % client)
            print('remove issued')
            os.system('rm -f "pki/issued/%s.crt"' % client)
            os.system('rm -f /etc/openvpn/crl.pem')
            os.system('cp /etc/openvpn/easy-rsa/pki/crl.pem /etc/openvpn/crl.pem')
            os.system('chmod 644 /etc/openvpn/crl.pem')
            os.system('find /home/ -maxdepth 2 -name "%s.ovpn" -delete' % client)
            os.system('rm -f "/etc/openvpn/vpn_clients/%s.ovpn" ' % client)
            os.system('rm -f "/etc/openvpn/vpn_clients/%s.info" ' % client)
            os.system('sed -i "s|^%s,.*||" /etc/openvpn/ipp.txt' % client)
            print ("Removed %s.ovpn and %s.info from /etc/openvpn/vpn_clients." % (client, client))
            print ("Certificate for client %s revoked." % client)
        else:
            print ("\nClient not found! Continuing to next client...\n")
            continue 

def create_client():
    for name,last,email in userdata:
        space = ( ' ' * 10)
        if os.path.isfile('/etc/openvpn/easy-rsa/pki/reqs/%s.req' % name):
            print("File already exist, going to next client...")
            continue
        print (name,last,email)
        print ("\n" + space + "----- Creating config for '%s' -----" % name)
        
        # Generating random password 4 words long, using mkpasswd.py as the source for the list
        listcount = len(pwlist)
        num_words = 4
        chosen_words = []
        while len(chosen_words) < num_words:
            choice = random.randrange(listcount)
            if choice in chosen_words:
                continue
            else:
                chosen_words.append(pwlist[choice])
        password = " ".join(chosen_words)
        
        # Change directory to run easyrsa script
        os.chdir('/etc/openvpn/easy-rsa')
        # Runs easyrsa arugment build-client-full and takes in the user name, then the stdin uses
        # the random generated password to push to PEM passpharse for client
        os.system(' echo "%s" ; echo "%s" | ./easyrsa build-client-full %s ' % ( password, password, name))
        
        # newfile made for client cert and  moved cert info to %s.ovpn
        newfile = open('/etc/openvpn/vpn_clients/%s.ovpn' % name, "w")
        copyfile('/etc/openvpn/client-template.txt', '/etc/openvpn/vpn_clients/%s.ovpn' % name)
        file = open('/etc/openvpn/vpn_clients/%s.ovpn' % name, "a")
        
        # Set an IP the user will receive
        address = None # Need to give a range of IPS, then send the client to /etc/openvpn/ccd
        
        # Read cert for server
        cert = open("/etc/openvpn/easy-rsa/pki/ca.crt","r")
        key1 = cert.read()
        cert.close()
        # Read cert for client 42-53
        cert =  open("/etc/openvpn/easy-rsa/pki/issued/%s.crt" % name, "r")
        lines = cert.readlines()
        lines = lines[41:53]
        key2 = ''.join(lines)
        cert.close()
        # Read cert key
        cert = open("/etc/openvpn/easy-rsa/pki/private/%s.key" % name, "r")
        key3 = cert.read()
        cert.close()
        cert = open("/etc/openvpn/tls-crypt.key","r")
        key4 = cert.read()
        cert.close()
        with open('/etc/openvpn/vpn_clients/%s.ovpn' % name, mode='a') as cert:
                cert.write('\n<ca>\n')
                cert.write(key1)
                cert.write('</ca>\n')
                cert.write('\n<cert>\n')
                cert.write(key2)
                cert.write('</cert>\n')
                cert.write('\n<key>\n')
                cert.write(key3)
                cert.write('</key>\n')
                cert.write('\n<tls-crypt>\n')
                cert.write(key4)
                cert.write('</tls-crypt>\n')
                
        # Information for client, including: name, lastnaem, email, and password
        client_info = open('/etc/openvpn/vpn_clients/%s.info' % name, "w")
        with open('/etc/openvpn/vpn_clients/%s.info' % name, mode='a') as info:
            info.write('OpenVPN client information:\n------------------------------------')
            info.write('\nUsernmaer: ' + name + '\nLastname: ' + last + '\nEmail: ' + email)
            info.write('\nPassword: %s ' % password + '\n------------------------------------\n')

        # Email out the ovpn files and information.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create", dest="clientFile", help="Open specified file to add clients")
    parser.add_argument("-r", "--revoke", dest="revokeFile", help="Open specified file to remove clients")
    parser.add_argument("-s", "--show",   action='store_true', help="Displays total number and names of active clients")
    args = parser.parse_args()
    clientFile = args.clientFile
    revokeFile = args.revokeFile
         
    #"Argument is = to -c or --create do:"
    if args.clientFile: 
        global userdata
        with open(clientFile) as f:
            userdata = [x.strip().split(',') for x in f.readlines()]
        create_client()
    #"Argument is = to -r or --revoke do:"
    elif args.revokeFile:  
        global removedata
        with open(revokeFile) as f:
            removedata = f.read().splitlines()
        revoke_client()
    #"Argument is = to -s or --show do:"
    elif args.show:
        check_client()

main()
