import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from subprocess import Popen, PIPE, STDOUT
import email.utils
from email.utils import formatdate

#Take in a email-template file and use that to choose what email server to hit
#Will use a flag to determine the file
#flag_email = parameter -e <template from console>
#email_template = open(flag_email, "r")
#email_template = emtemp.read()

def sendit(username,name, last, to_email, password,server=None, url=None):

    if server == "PvJ":
        # PVJ
        print("Using PvJ mail server")

        mailserver = "smtp.gmail.com"
        mailport = 587
        sender_passwd = ""
        #sender_passwd = ""
        fr_email = "noreply@prosversusjoes.net"
        reply_email = "dichotomy@prosversusjoes.net"
        subj = "Your OpenVPN credentials for Pros V Joes"

        email_template= """ %s %s - Here are your Username and PEM Password for VPN access.
        Please use the attached OVPN file.

        OpenVPN Credentials:
        Username:  %s
        Password:  %s

        Test your connection:
            ping 10.20.30.1
            ping google.com

        
        Install Openvpn 2.5.4: 
        NOTE: This is an older release, make sure you get the correct version
            Windows - Install Openvpn 2.5.4 https://openvpn.net/community-downloads/
            Linux   - Use OS package manager. run 'sudo openvpn --config <client.ovpn>'
            Mac     - Install Tunnelblick https://tunnelblick.net/

        Good luck and have fun =)
        """ 
    elif server == "cyberwildcats":
        # Cyberwildcats
        
        mailserver = "smtp.gmail.com"
        mailport = 587
        sender_passwd = ""
        #sender_passwd = ""
        fr_email = "noreply@prosversusjoes.net"
        #reply_email = "dichotomy@prosversusjoes.net"
        ################################################
        #mailserver = "10.20.31.75"
        #fr_email = "earnoth@cyberwildcats.net"
        reply_email = "eric.i.arnoth@wilmu.edu"
        subj = "Your OpenVPN credentials for Cyberwildcats"

        email_template="""%s %s - Here are your Username and PEM Password for VPN access.
        Please use the attached OVPN file.

        OpenVPN Credentials:
        Username:  %s
        Password:  %s

        Test your connection:
            ping 10.20.30.1
            ping google.com

        Install Openvpn 2.5.4:
        NOTE: This is an older release, make sure you get the correct version.

            Windows - Install Openvpn 2.5.4 https://openvpn.net/community-downloads/
            Linux   - Use OS package manager. run 'sudo openvpn --config <client.ovpn>'
            Mac     - Install Tunnelblick https://tunnelblick.net/

        If you have any questions or issues, please reach out to #vpn_troubleshooting channel on the Cyberwildcats Slack.

        """
        if url:
            email_template += "\r\nYou can also retreive your OVPN file from this URL: %s" % url
    print("Constructing mail configs")
    body = email_template % (name, last, username, password)
    body = MIMEText(body)
    msg = MIMEMultipart()
    msg['Subject'] = subj
    msg['From'] = fr_email
    msg['To'] = to_email
    msg['BCC'] = reply_email
    msg['Reply-to'] = reply_email
    msg['Date'] = email.utils.formatdate(localtime=True)

    attached_config = MIMEBase('application', "octet-stream")
    attached_config.set_payload(open("/etc/openvpn/vpn_clients/%s.ovpn" % username, "rb").read())
    encoders.encode_base64(attached_config)

    attached_config.add_header('Content-Disposition', 'attachment; filename="%s.ovpn"' % username)
    print("Attaching config and info files to email")

    msg.attach(body)
    msg.attach(attached_config)
    print("Preparing email to be sent")
    s = smtplib.SMTP(mailserver, mailport)
    print("Establishing a safe connection")
    s.starttls()
    print("logging into core email account")
    s.login(fr_email, sender_passwd)
    print( "Forward email being used: %s" % fr_email)
    print( "Sending mail to: %s" % to_email)

    s.sendmail(fr_email, [reply_email, to_email], msg.as_string())
    s.quit()

