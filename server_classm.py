import socket
import threading
import pickle
import time
import pygame
from pygame import mixer
from pygame.locals import *

def start_thread(fun,args):
    threading.Thread(target=fun,args = args).start()


class Server:
    def __init__(self,passward = "123a"):
        self.HEADER_LEN = 30
        self.read = 1   
        self.RUN = True

        self.messages = {"Server":{"sent":True,"message":{"prpse":"","msg":"","from":"Server"}}}    #message format: {client:[is_sent,(message,username)],  ,  ,  ,  ,  ,  ,  ,  }
        self.clients = []     #stores [client_socket,IP,User_name,running]
        self.connected = {}   #{client:{"send":True,"receive":True},     ,     ,   ,}
        self.thrds = []

        self.passward = passward
        print(passward)
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


    def process_message(self,msg):       
        msg = pickle.dumps(msg)
        padding = len(msg)%self.HEADER_LEN
        if (padding!=0):
            msg+=bytes((" "*(self.HEADER_LEN - padding) ),"utf-8")
        units = len(msg)//self.HEADER_LEN                                            #it is just the message length without the header file
        #print(len(msg)%self.HEADER_LEN)
        msg = bytes(f"{units:<{self.HEADER_LEN}}","utf-8")+msg
        #print(units,len(msg)%self.HEADER_LEN)
        #print("Sending msg:",msg)
        return msg
    
    def accept_clients(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((socket.gethostname(),1234))
        self.server.listen(5)  
        thrd = threading.Thread(target=self.send_all)            #Thread 1(sending)
        thrd.start()
        thrd.name = "Send_all"
        self.thrds.append(thrd)
        threading.Thread(target=self.prnt).start()
        while True:
            print("Accepting")
            client = self.server.accept()
            #get id and passward
            start_thread(self.verify,(client,))
            print(self.clients)
          
    def verify(self,client):
        while True:
            try:              #if send to all then get new message from the client
                full_msg = self.recv(client[0])
                #print(full_msg)
                full_msg= full_msg["msg"]
                
                if full_msg:
                    #print(full_msg ,"is this.")
                    if (full_msg != self.passward):
                        client[0].send(bytes("No ","utf-8"))
                        client[0].close()
                        print("Wrong passward!! connection lost!!")
                        break
                    else:
                        client[0].send(bytes("Yes","utf-8"))
                        print("correct passward!!")
                        threading.Thread(target=self.user_name,args=(client,)).start()
                        break
            except:
                break

    def user_name(self,client):
        while True:               #if send to all then get new message from the client
            try:              #if send to all then get new message from the client
                user_name = self.recv(client[0])["msg"]
                if user_name:
                    client = list(client)
                    client.append(user_name)
                    client = tuple(client)
                    self.clients.append(client)           #adds username to client tuple
                    self.messages[client] = {"sent":True,"message":{"prpse":"","msg":"","from":client[2]}}
                    self.connected[client] = {"send":True,"receive": True}
                    print("Client Name saved.  You are ready to go.")

                    client[0].send(self.process_message({'prpse': (0,), 'msg': 'Welcome to the local network.' ,'from': "Server"}))        #Welcome message
                    thrd = threading.Thread(target=self.receive,args=(client,))       #receiving threads
                    thrd.start() 
                    thrd.name = client[2]
                    self.thrds.append(thrd)
                    print(f"Connection from {client[2]} is accepted.")
                    break
            except:
                print("Client Disconnected...")
                if client in self.clients:
                    self.clients.remove(client)
                break

    def recv(self,client):
        full_msg =b""
        units= 0
        try:
            msg = client.recv(self.HEADER_LEN)
            #print(msg)
            units =int(msg)
            while (units>self.read):
                msg = client.recv(self.HEADER_LEN*self.read)
                full_msg+=msg
                #print(full_msg)
                units-=self.read
            else:
                msg = client.recv(self.HEADER_LEN*self.read)
                full_msg+=msg
                #print(full_msg)
                #print(msg,"\n\n\n\n")
                
                full_msg = pickle.loads(full_msg.rstrip())
                #print("Received msg:",full_msg)
                return full_msg
        except:
            self.connected[client]["receive"] = False
            if self.connected[client]["send"] == False:
                self.clients.remove(client)
                self.connected.pop(client)
                self.messages.pop(client)

            print(client[2],"is disconnected from server")
            all_thrds = self.thrds
            for i in all_thrds:
                if i.name == client[2]:
                    self.thrds.remove(i)

            return

    def receive(self,client):
        while self.connected[client]["receive"]:
            if (self.messages[client]["sent"] == True): 
                try:              #if send to all then get new message from the client
                    full_msg = self.recv(client[0])
                    #print(full_msg)
                    if full_msg:    
                        #print(full_msg)
                        self.messages[client] = {"sent":False,"message":{"msg":full_msg["msg"],"prpse":full_msg["prpse"],"from":client[2]}}        #This is the final message received
                        #print("Received "," \n")
                        #print(f"All messages:{messages}")
                except:
                    self.connected[client]["receive"] = False
                    if self.connected[client]["send"] == False:
                        self.clients.remove(client)
                        self.connected.pop(client)
                        self.messages.pop(client)
                    print(client[2],"is disconnected from server")

                    all_thrds = self.thrds
                    for i in all_thrds:
                        if i.name == client[2]:
                            self.thrds.remove(i)
                    break

    def send_all(self):
        while True:
            copy_messages = self.messages.copy()
            all_clients = self.clients

            for i in copy_messages:
                if (copy_messages[i]["sent"] == False):
                    for client in all_clients:
                        try:
                            if (client!= i and self.connected[client]["send"] ==True):
                                client[0].send(self.process_message(copy_messages[i]["message"]))   #send the message and client name
                        except:
                            print("sending error to client:",client[2])
                            self.connected[client]["send"] =False
                            if self.connected[client]["receive"] == False:
                                self.clients.remove(client)
                                self.connected.pop(client)
                                self.messages.pop(client)
                                all_thrds = self.thrds
                                for i in all_thrds:
                                    if i.name == client[2]:
                                        self.thrds.remove(i)

                    self.messages[i] = {"sent":True,"message":{"msg":"","prpse":"","from":client[2]}}
                    try:
                        i[0].send(self.process_message({"prpse":(3,),"msg":"Sent","from":i[2]}))
                    except:
                        pass
                    #print(f"sent ")

                    #print(self.messages[i])
                    # except:
                    #     print("Sending error")
                    #     all_clients.remove(1)
                    #     pass

    def prnt(self):
        while True:
                print("total clients:",len(self.clients),"threads:",len(self.thrds))
                print()
                time.sleep(5)



srvr = Server()
start_thread(srvr.accept_clients,())






""" screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

while True:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            pygame.quit()
            break
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.circle(screen,(100,100,100),mouse_pos,10)
    pygame.display.update() """