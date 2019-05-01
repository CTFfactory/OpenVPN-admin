# OpenVPN installer
Installs OpenVPN community verison
<ul>
<li>Installs all needed dependencies</li> 
<li>Sets up Easyrsa</li>  
<li>Downloads mkclient.py for automation client creation/deletion</li> 
</ul>

## Step 1: Download repo
Git clone https://github.com/huzar01/OpenVPN

## Step 2: Run installer 
Run **openvpn-install.sh** <br />
This will install openvpn, easy-rsa, and create the required directories 
## Step 3: Add routes to server.conf
Configure routes on VPN server:<br />
![alt text](https://i.imgur.com/HW4XXZx.png)


Edit server.conf to add routes -> **/etc/openvpn/server.conf**:<br />
#### server.conf<br />
![alt text](https://i.imgur.com/9f2b9R9.png)

Default client template located -> **/etc/openvpn/client-template.txt**<br />
mkclient.py uses this to create client configs<br />
IF USING ON WINDOWS COMMENT OUT **setenv opt block-outside-dns**<br />
#### client-template.txt<br />
![alt text](https://i.imgur.com/y53wgTP.png)

## Step 4: Create client data [First,Last,Email]
Add clients you want  to create in client-creation.txt” -> **/etc/openvpn/client-creation.txt** <br />
*A default template is created with user John* <br />
**FORMAT IS IMPORTANT!!!**<br />
**John,Doe,JohnD@example.com**
#### client-creation.txt<br />
![alt text](https://i.imgur.com/PklKVq0.png)


## Step 5: Run mkclient.py to create clients configuration 
mkclient.py -h <br />
![alt text](https://i.imgur.com/zotsrzy.png)

Create the client users:<br />
**mkclient.py -c client-creation.txt**<br />
Mkclient.py can use any text file that contains the correct format (client-creation.txt is the default)<br />

To remove clients:<br />
Add the client names to client-remove.txt -> /etc/openvpn/client-remove.txt<br />
*A default client-remove.txt is created with user John* <br />
**mkclient.py -r client-remove.txt** <br />
You can create your own text file (client-remove.txt is the default)<br />

## Credit 
Credit to angristan and Nyr, installer is a modified version of angristan openvpn-install<br />
