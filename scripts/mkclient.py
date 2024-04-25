#!/usr/bin/env python3
import sys,os,shutil,subprocess,random,argparse
from datetime import date
from shutil import copyfile
from random import randrange
from mkpasswd import pwlist
from mkemail import sendit

'''
Generate clients with cert and password authentication 
Script takes one arugement being a text file with 3 variables delimited by commas(,)
EX: matt,young,matty01@example.com
Uses easyrsa to create a client.ovpn config with a cert and randomly generated password, using a list from mkpasswd.py 
Information about client is stored in /etc/openvpn/vpn_clients/

To use cyberwildcats email use the -S <cyber> flag, default without the flag is PVJ email

'''

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

def remove_client(removedata):
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

def disable_client(removedata):
    for client in removedata:
        os.chdir('/etc/openvpn/')
        #check if client name is in authorized_users already
        f = open('/etc/openvpn/authorized_users')
        authorized = (f.read())

        if ('#'+client) in authorized and client == client:
            print("\nClient:%s is already disabled!" % client)
        elif client not in authorized:
            print("\nClient:%s not found!" % client)
        else:
            print("\nDisabled Client: %s" % client)
            #client.replace("%s","#%s" % (client,client)) 
            #os.system('sed -i -e "s/\b%s\b/#%s/g" "/etc/openvpn/authorized_users" ' % (client,client)) 
            os.system('sed -i -e "s/^%s$/#%s/g" "/etc/openvpn/authorized_users" ' % (client,client))

def enable_client(removedata):
    for client in removedata:
        #print(client)
        os.chdir('/etc/openvpn/')
        #check if client name is in authorized_users already
        f = open('/etc/openvpn/authorized_users')

        authorized = (f.read())
        if (client) in authorized:
            print("\nEnabled Client: %s" % client)
            os.system('sed -i -e "s/^#%s$/%s/g" "/etc/openvpn/authorized_users" ' % (client,client))
            #client.replace("%s","#%s" % client) 
        else:
            print("\nClient:%s not found!" % client)
            continue

def push_ovpn(ovpn_filename):
    ssh = "/usr/bin/ssh"
    scp = "/usr/bin/scp"
    user = "earnoth"
    host = "10.20.31.78"
    root_path = "/var/www/"
    class_dir = "sec450"
    source_dir = "/etc/openvpn/vpn_clients"
    student_dir = str(random.random())[2:9]
    web_dir = "%s/%s/%s" % (root_path, class_dir, student_dir)
    destination = "%s@%s" % (user, host)
    ssh_cmd = [ssh, destination, "mkdir", web_dir]
    ssh_output = subprocess.run(ssh_cmd)
    print(ssh_output)
    scp_source = "/".join([source_dir, ovpn_filename])
    scp_destination = "".join([destination, ":", web_dir, "/"])
    scp_cmd = [scp, scp_source, scp_destination]
    scp_output = subprocess.run(scp_cmd)
    print(scp_output)
    input("Press ENTER to continue")
    url = "http://www.cyberwildcats.net/%s/%s/%s" % (class_dir, student_dir, ovpn_filename)
    return url

def create_client(userdata,server,sec450=False,noemail=False):
    for name,last,twitter,to_email,role in userdata:
        #print("###############################################################")
        #print(name + '\n' + last + '\n' + twitter + '\n' + to_email + '\n' + role)
        #print("###############################################################")
        
        name = name.lower().strip()
        last = last.lower().strip()
        to_email = to_email.lower()  
        email_parts = to_email.split('@',1)
        username = name+"."+last+"."+email_parts[0]
        year = str(int(date.today().year) + 3)
        fullname=".".join([username, year])
       
        space = ( ' ' * 10)
        if os.path.isfile('/etc/openvpn/easy-rsa/pki/reqs/%s.req' % fullname):
            print("Client already exists -> {} ".format(fullname))
            continue
        print (name,last,to_email)
        print ("\n" + space + "----- Creating config for '%s' -----" % fullname)
        
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
        os.system('echo "%s" ; echo "%s" | ./easyrsa build-client-full %s' % (password,password,fullname))
        
        # newfile made for client cert and  moved cert info to %s.ovpn
        newfile = open('/etc/openvpn/vpn_clients/%s.ovpn' % fullname, "w")
        copyfile('/etc/openvpn/client-template.txt', '/etc/openvpn/vpn_clients/%s.ovpn' % fullname)
        file = open('/etc/openvpn/vpn_clients/%s.ovpn' % fullname, "a")
        
        # Set an IP the user will receive
        address = None # Need to give a range of IPs, then send the client to /etc/openvpn/ccd
        
        # Read cert for server
        cert = open("/etc/openvpn/easy-rsa/pki/ca.crt","r")
        key1 = cert.read()
        cert.close()
        # Read cert for client 42-53
        cert =  open("/etc/openvpn/easy-rsa/pki/issued/%s.crt" % fullname, "r")
        lines = cert.readlines()
        lines = lines[41:54]
        key2 = ''.join(lines)
        cert.close()
        # Read cert key
        cert = open("/etc/openvpn/easy-rsa/pki/private/%s.key" % fullname, "r")
        key3 = cert.read()
        cert.close()
        cert = open("/etc/openvpn/tls-crypt.key","r")
        key4 = cert.read()
        cert.close()
        ovpn_filename = "%s.ovpn" % fullname
        with open('/etc/openvpn/vpn_clients/%s' % ovpn_filename, mode='a') as cert:
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
        client_info = open('/etc/openvpn/vpn_clients/%s.info' % fullname, "w")
        with open('/etc/openvpn/vpn_clients/%s.info' % fullname, mode='a') as info:
            info.write('OpenVPN client information:\n------------------------------------')
            info.write('\nFirstname: ' + name + '\nEvent: ' + last + '\nEmail: ' + to_email)
            info.write('\nRole: ' + role + '\nTwitter: ' + twitter)
            info.write('\n------------------------------------' + '\nUsername: ' + fullname)
            info.write('\nPassword: %s ' % password + '\n------------------------------------\n')
        os.system(' echo "%s" >> "/etc/openvpn/authorized_users" ' % fullname)
        
        if sec450:
            url = push_ovpn(ovpn_filename)
            if noemail:
                pass
            else:
                sendit(fullname, name, last, to_email, password, server, url)
        # Sends credentials and .ovpn to the specific email grabbed from the given textfile
        else:
            if noemail:
                pass
            else:
                print("Sending Client email with creds")
                sendit(fullname, name, last, to_email, password, server)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create", dest="clientFile", help="./mkclient.py -c userlist.txt <First,Last,Twiter,Email,Role>")
    parser.add_argument("-r", "--revoke", dest="removeFile", help="Open specified file to remove clients")
    parser.add_argument("-d", "--disable", dest="disableFile", help="Open specified file to disable clients")
    parser.add_argument("-e", "--enable", dest="enableFile", help="Open specified file to enable clients")
    parser.add_argument("-s", "--show",   action='store_true', help="Displays total number and names of active clients")
    parser.add_argument("-S", "--server", default=None,  dest='server', help="Selects the email server")

    parser.add_argument("--sec450", dest="sec450", action='store_true', default=False, 
                                help="push OVPN files to cyberwildcats.net and send proper emails")
    parser.add_argument("--noemail", dest="noemail", action='store_true', default=False,
                                help="Do not send emails upon account generation")

    args = parser.parse_args()
    clientFile = args.clientFile
    disableFile = args.disableFile
    enableFile = args.enableFile
    removeFile = args.removeFile
    server = args.server
    sec450 = args.sec450
    noemail = args.noemail

    #"Argument is = to -c or --create do:"
    if args.clientFile:
        with open(clientFile) as f:
            userdata = [x.strip().split(',') for x in f.readlines()]
        if server == "cyberwildcats" or server == "PvJ":
            create_client(userdata,args.server,sec450,noemail)
        else:
            sys.exit("invalid option, --server option must be 'cyberildcats' or 'PvJ'")
    #"Argument is = to -r or --revoke do:"
    elif args.removeFile:
        with open(removeFile) as f:
            removedata = f.read().splitlines()
        remove_client(removedata)
    #"Argument is = to -d or --disable do:"
    elif args.disableFile:
        with open(disableFile) as f:
            removedata = f.read().splitlines()
        disable_client(removedata)
    
    #"Argument is = to -e or --enable do:"
    elif args.enableFile:
        with open(enableFile) as f:
            removedata = f.read().splitlines()
        enable_client(removedata)
    #"Argument is = to -s or --show do:"
    elif args.show:
        check_client()
    else:
        print("Please add a flag with the correct text file as an arguement")

main()

