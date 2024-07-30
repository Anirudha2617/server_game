import socket
import pickle
import threading
import time
import tkinter as tk

class Client:
    def __init__(self):

        self.HEADER_LEN = 30
        self.read = 2
        self.running = False
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print(socket.gethostname())
        self.sending = True

        #Constants
        self.messages = [{"prpse":(0,),"msg":"Welcome to the local network1."},{"prpse":(0,),"msg":"Welcome to the local network2."},{"prpse":(0,),"msg":"Welcome to the local network3."},{"prpse":(0,),"msg":"Welcome to the local network4."}]
        self.received_message = []
        self.thrds = []
        # self.start( "123a","Gaanesha")
    
    def screen(self):
        

        self.client.connect(("Anirudha_Sahu",1234))


        self.Window = tk.Tk()
        self.Window.withdraw()

        self.login = tk.Toplevel()

        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=350)

        self.pls = tk.Label(self.login, 
                            text="Please Login to a chatroom", 
                            justify=tk.CENTER,
                            font="Helvetica 12 bold")

        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)

        self.userLabelName = tk.Label(self.login, text="Username: ", font="Helvetica 11")
        self.userLabelName.place(relheight=0.2, relx=0.1, rely=0.25)

        self.Username = tk.Entry(self.login, font="Helvetica 12")
        self.Username.place(relwidth=0.4 ,relheight=0.1, relx=0.35, rely=0.30)
        self.Username.focus()

        self.roomLabelName = tk.Label(self.login, text="Room Id: ", font="Helvetica 12")
        self.roomLabelName.place(relheight=0.2, relx=0.1, rely=0.40)

        self.passward = tk.Entry(self.login, font="Helvetica 11", show="*")
        self.passward.place(relwidth=0.4 ,relheight=0.1, relx=0.35, rely=0.45)
        
        self.go = tk.Button(self.login, 
                            text="CONTINUE", 
                            font="Helvetica 12 bold", 
                            command = lambda: self.start( self.passward.get(),self.Username.get()))
        
        self.go.place(relx=0.35, rely=0.62)

        self.Window.mainloop()

    def start(self,passward,Username):
    #ask for the passward
        self.passward = passward
        self.username = Username
        passward = passward
        passward = self.process_message(passward)

        self.client.send(passward)

        try:
            while True:
                msg = self.client.recv(3).decode("utf-8")
                if msg == "No ":
                    print("Wrong passward!! Try again.")
                    exit(0)
                elif (msg == "Yes"):
                    break
        except:
            print("Connection error!!")
            

        Username = self.process_message(Username)
        self.client.send(Username)

        time.sleep(1)            #time for server to create object
        self.login.destroy()

        #create 2 threads for send and receive
        #create a dict for received message

        #send thread

        thrd = threading.Thread(target=self.receive)
        thrd.start()
        self.thrds.append(thrd)


        #Receive thread
        thrd = threading.Thread(target=self.send)
        thrd.start()
        self.thrds.append(thrd)

        time.sleep(1)

        self.running = True
    #Functions
    def process_message(self,msg,prpse = (0,)):
        #print("Send mesage :",msg)
        msg = {"prpse":prpse,"msg":msg}
        msg = pickle.dumps(msg)
        padding = len(msg)%self.HEADER_LEN
        if (padding!=0):
            msg+=bytes((" "*(self.HEADER_LEN - padding) ),"utf-8")
        units = len(msg)//self.HEADER_LEN                                            #it is just the message length without the header file
        #print(len(msg)%self.HEADER_LEN)
        msg = bytes(f"{units:<{self.HEADER_LEN}}","utf-8")+msg
        #print(units,len(msg)%(self.HEADER_LEN*self.read))
        return msg

    def recv(self,client):
        full_msg =b""
        try:
            msg = client.recv(self.HEADER_LEN)
            units =int(msg)
            #print(msg)
        except:
            #print("no message")
            return
        while (units>self.read):
            msg = client.recv(self.HEADER_LEN*self.read)
            full_msg+=msg
            units-=self.read
        else:
            msg = client.recv(self.HEADER_LEN*self.read)
            full_msg+=msg
            # print(len(full_msg))
            full_msg = pickle.loads(full_msg.rstrip())
            #print("Received msg:",full_msg)
            return full_msg

    def receive(self):
        #print("receive started")
        while True:
            full_msg =self.recv(self.client)
            if full_msg:
                #print("received:",full_msg,self.sending )
                if (full_msg["from"] == self.username):
                    #print("in",len(self.messages))
                    self.sending =True
                    
                else:
                    #print("Appended")
                    self.received_message.append(full_msg)
        
    def send(self):
        while True:

            if self.sending:
                try:
                    i = self.messages.pop(0)
                    msg = self.process_message(i["msg"],i["prpse"])
                    self.client.send(msg)
                    #print("Sent:",i["msg"])
                    self.sending = False
                except:
                    pass
                

            #time.sleep(1)

