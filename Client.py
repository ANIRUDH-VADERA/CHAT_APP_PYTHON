# Importing the socket module
import socket
# For distributing the messsages along all clients
import select
# When no message recieved or any other communication error
import errno
import sys
# For realtime updation of state
import threading

# AF_INET - IPv4 Connection
# SOCK_STREAM - TCP Connection
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# IPv4 to be used
# The port to which the client wants to connect
IP = "127.0.0.1"
port = 3000 

# Defining the HeaderSize of each message to be recieved 
HEADERSIZE = 10

# The client userName
my_userName = input("UserName : ")

# Connect to the server on this machine or locally
# socket.gethostname() to get the hostname of the server
clientSocket.connect((IP,port))
# No blocking the incoming messages
clientSocket.setblocking(False)

# Sending the username to the server
userName = my_userName.encode()
userNameHeader = f"{len(userName):<{HEADERSIZE}}".encode()
clientSocket.send(userNameHeader + userName)

# recieving chunks of data from the server
def recieveData():
    flag = 0
    # Recieving things infinitely
    while True:
        try:
            if(flag == 0):# For the initial informative message
                initHeader = clientSocket.recv(HEADERSIZE)
                initLength = int(initHeader.decode().strip())
                msg = clientSocket.recv(initLength).decode()
                print(f"Server > {msg}")
                flag = 1
            else:# For the subsequent messages
                userNameHeader = clientSocket.recv(HEADERSIZE)
                if not len(userNameHeader):
                    print("Connection closed by the Server")
                    sys.exit()
                userNameLength = int(userNameHeader.decode().strip())
                userName = clientSocket.recv(userNameLength).decode()
                
                messageHeader = clientSocket.recv(HEADERSIZE)
                messageLength = int(messageHeader.decode().strip())
                message = clientSocket.recv(messageLength).decode()
                
                print(f"{userName} > {message}")
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if(e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK):
                print("Reading Error",str(e))
                sys.exit()
            continue
        except Exception as e:
            print("General error",str(e))
            sys.exit()

# Writing the data and sending it         
def writeData():
    while True:
        message = input("")
        
        if message:
            message = message.encode()
            messageHeader = f"{len(message):<{HEADERSIZE}}".encode()
            
            clientSocket.send(messageHeader + message)

recieveThread = threading.Thread(target = recieveData)
recieveThread.start()
            
writeThread = threading.Thread(target = writeData)
writeThread.start()