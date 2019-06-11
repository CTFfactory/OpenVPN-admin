#!/usr/bin/env python3
import sys,os,shutil,subprocess,random,argparse
from shutil import copyfile
from random import randrange
from mkpasswd import pwlist
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from subprocess import Popen, PIPE, STDOUT
import email.utils
from email.utils import formatdate

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

def remove_client():
    for client in removedata:
        print (client)
        # easyrsa function that revokes client cert
        os.system('tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d "=" -f 2 > /etc/openvpn/rc-names.txt' )
        f = open('/etc/openvpn/rc-names.txt', 'r')
        list_clients = (f.read())
        f.close()
        if client in list_clients:
            newpath = ('/etc/openvpn/graveyard/%s' % client)
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            os.chdir('/etc/openvpn/easy-rsa')
            os.system('./easyrsa --batch revoke "%s"' % client)
            os.system('EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl')
            # Not important just send sout updated crl to this folder
            
            os.system('cp /etc/openvpn/easy-rsa/pki/crl.pem /etc/openvpn/revoked_certs')
            print('moved req')
            os.system('mv "pki/reqs/%s.req" /etc/openvpn/graveyard/%s' % (client,client))
            print('moved private')
            os.system('mv "pki/private/%s.key" /etc/openvpn/graveyard/%s' % (client,client))
            print('moved issued')
            os.system('mv "pki/issued/%s.crt" /etc/openvpn/graveyard/%s' % (client,client))
            os.system('rm /etc/openvpn/crl.pem')
            os.system('cp /etc/openvpn/easy-rsa/pki/crl.pem /etc/openvpn/crl.pem')
            os.system('chmod 644 /etc/openvpn/crl.pem')
#            os.system('find /home/ -maxdepth 2 -name "%s.ovpn" -delete' % client)
            os.system('mv "/etc/openvpn/vpn_clients/%s.ovpn" /etc/openvpn/graveyard/%s' % (client,client))
            os.system('mv "/etc/openvpn/vpn_clients/%s.info" /etc/openvpn/graveyard/%s' % (client,client))
            os.system('sed -i "s|^%s,.*||" /etc/openvpn/iplist.txt' % client)
            os.system('sed -i "s/%s//g" /etc/openvpn/authorized_users' % client)            
            os.system('sed -i "/^$/d" /etc/openvpn/authorized_users')
            print ("Removed %s from authorized_users" % client)
            print ("moved  %s.ovpn and %s.info from /etc/openvpn/graveyard." % (client, client))
            print ("Certificate for client %s revoked." % client)
        else:
            print ("\nClient not found! Continuing to next client...\n")
            continue

def disable_client():
    for client in removedata:
        os.chdir('/etc/openvpn/')
        #check if client name is in authorized_users already
        f = open('/etc/openvpn/authorized_users')
        
        authorized = (f.read())
        if ('#'+client) in authorized:
            print("\nClient:%s is already disabled!" % client)
        elif client not in authorized:
            print("\nClient:%s not found!" % client)
        else:
            print("\nClient:%s now disabled!" % client)
            #os.system('echo "%s" >> "/etc/openvpn/authorized_users"' % client)
            os.system('sed -i -e "s/%s/#%s/g" "/etc/openvpn/authorized_users" ' % (client,client)) 
    
    #print(authorized)

def enable_client():
    for client in removedata:
        #print(client)
        os.chdir('/etc/openvpn/')
        #check if client name is in authorized_users already
        f = open('/etc/openvpn/authorized_users')
        
        authorized = (f.read())
        if (client) in authorized:
            print("\nEnabled Client: %s" % client)
            os.system('sed -i -e "s/#%s/%s/g" "/etc/openvpn/authorized_users" ' % (client,client)) 
            
        else:
            print("\nClient:%s not found!" % client)
            continue 
    #print(authorized)

def create_client():
    for name,last,to_email,role in userdata:
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
        os.system('echo "%s" ; echo "%s" | ./easyrsa build-client-full %s' % (password,password,name))
        
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
            info.write('\nUsername: ' + name + '\nLastname: ' + last + '\nEmail: ' + to_email)
            info.write('\nPassword: %s ' % password + '\n------------------------------------\n')
        os.system(' echo "%s" >> "/etc/openvpn/authorized_users" ' % name)
        
        # Sends credentials and .ovpn to the specific email grabbed from the given textfile
        sendit(name, last, to_email, password)

def sendit(name, last, to_email, password):
    # Email Server 
    # 10.20.31.78 = cyberwildcats.net
    # 10.20.31.75 = prosversusjoes.net

#    emtemp = open("/etc/openvpn/email-template.txt", "r")
#    email_template = emtemp.read()

    
    
    mailserver = "10.20.31.75"
    #mailserver = "10.20.31.78"
    fr_email = "dichotomy@prosversusjoes.net"
    #fr_email = "earnoth@cyberwildcats.net"
    #reply_email = "eric.i.arnoth@wilmu.edu"
    reply_email = "dichotomy@prosversusjoes.net"
    subj = "Your OpenVPN credentials for Cyberwildcats"
    
    email_template="""%s %s - here is your Username and PEM Password for VPN access.

    OpenVPN Credentials:
    Username:  %s
    Password:  %s
    

    """

    body = email_template % (name, last, name, password)
    body = MIMEText(body)
    msg = MIMEMultipart()
    msg['Subject'] = subj
    msg['From'] = fr_email
    msg['To'] = to_email
    msg['BCC'] = reply_email
    msg['Reply-to'] = reply_email
    msg['Date'] = email.utils.formatdate(localtime=True)
    
    attached_config = MIMEBase('application', "octet-stream")
    attached_config.set_payload(open("/etc/openvpn/vpn_clients/%s.ovpn" % name, "rb").read())
    encoders.encode_base64(attached_config)

    attached_config.add_header('Content-Disposition', 'attachment; filename="%s.ovpn"' % name)

    msg.attach(body)
    msg.attach(attached_config) 
    
    s = smtplib.SMTP(mailserver)
    print( "Sending mail to %s" % to_email)
    s.sendmail(fr_email, [reply_email, to_email], msg.as_string())
    s.quit()
#    emtemp.close()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create", dest="clientFile", help="Open specified file to add clients")
    parser.add_argument("-r", "--revoke", dest="removeFile", help="Open specified file to remove clients")
    parser.add_argument("-d", "--disable", dest="disableFile", help="Open specified file to disable clients")
    parser.add_argument("-e", "--enable", dest="enableFile", help="Open specified file to enable clients")
    parser.add_argument("-s", "--show",   action='store_true', help="Displays total number and names of active clients")
    args = parser.parse_args()
    clientFile = args.clientFile
    disableFile = args.disableFile
    enableFile = args.enableFile
    removeFile = args.removeFile

    #"Argument is = to -c or --create do:"
    if args.clientFile:
        global userdata
        with open(clientFile) as f:
            userdata = [x.strip().split(',') for x in f.readlines()]
        create_client()
    #"Argument is = to -r or --revoke do:"
    elif args.removeFile:
        global removedata
        with open(removeFile) as f:
            removedata = f.read().splitlines()
        remove_client()
    #"Argument is = to -d or --disable do:"
    elif args.disableFile:
        with open(disableFile) as f:
            removedata = f.read().splitlines()
        disable_client()
    
    #"Argument is = to -e or --enable do:"
    elif args.enableFile:
        with open(enableFile) as f:
            removedata = f.read().splitlines()
        enable_client()
    #"Argument is = to -s or --show do:"
    elif args.show:
        check_client()
    else:
        print("Please add a flag with the correct text file as an arguement")

main()

