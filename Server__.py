# Importing the socket module
import socket
# For distributing the messsages along all clients
import select
# For realtime updation of state
import threading

# AF_INET - IPv4 Connection
# SOCK_STREAM - TCP Connection
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# For allowing reconnecting of clients
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Socket successfully created.")

# IPv4 to be used
# The Binding port no is reserved in my laptop
# Defining the HeaderSize of each message to be sent
IP = "127.0.0.1"  
port = 3000 
HEADERSIZE = 10

# Now we bind our host machine and port with the socket object we created
# The IPv4 address is given above
# The server is now listening for requests from other host machines also connected to the network
serverSocket.bind((IP,port))

#Listening to requests
serverSocket.listen()
print("Socket(Server) is currently active and listening to requests!!")

# Stores all those sockets which are connected
socketsList = [serverSocket]
# Client conected
clients = {}

# A function to recieve messages from the clients connected over the network
def recieveMessage(clientSocket):
    try:
        # We add some extra header information to our msg in order to know the size of the message we are sending
        # Getting the message header
        messageHeader = clientSocket.recv(HEADERSIZE)
        if not len(messageHeader):
            return False 
        # Decoding the message length
        messageLength = int(messageHeader.decode().strip())
        # Returning the message and its header
        return {"Header" : messageHeader , "Data" : clientSocket.recv(messageLength)}
    except: 
        return False

# Making a thread for every user connected to the server
def clientThread(notifiedSocket):
    while True:
        try:
            message = recieveMessage(notifiedSocket)
            
            # The part to do if a client leaves the connection
            if message is False:
                print(f"Closed Connection from {clients[notifiedSocket]['Data'].decode()}")
                socketsList.remove(notifiedSocket)
                del clients[notifiedSocket]
                break
            # This is the exiting condition if the user types exit@me he exists the connection
            if ((message["Data"].decode()) == "exit@me"):
                print(f"Closed Connection from {clients[notifiedSocket]['Data'].decode()}")
                socketsList.remove(notifiedSocket)
                del clients[notifiedSocket]
                break
            user = clients[notifiedSocket]
            print(f"Recieved message from {user['Data'].decode()} : {message['Data'].decode()}")
            
            # Distributing the Data to other clients
            for clientSocket in clients:
                if clientSocket != notifiedSocket:
                    clientSocket.send(user['Header'] + user['Data'] + message['Header'] + message['Data'])
        except:
            print(f"Closed Connection from {clients[notifiedSocket]['Data'].decode()}")
            socketsList.remove(notifiedSocket)
            del clients[notifiedSocket]
            break

# Function for server to send the message    
def writeData():
    while True:
        message = input("")
        # To ban a member
        if message== "ban@":
            ban_member = input("Enter the name of the member to ban :")
            
            for x in clients:
                if clients[x]["Data"].decode() == ban_member:
                    print(f"Closed Connection from {clients[x]['Data'].decode()}")
                    socketsList.remove(x)
                    del clients[x]
                    break
                    
            
        else: 
            if message:
                message = message.encode()
                messageHeader = f"{len(message):<{HEADERSIZE}}".encode()
                
                msg = {"Header" : messageHeader , "Data" : message}
                
                userName = "Server".encode()
                userNameHeader = f"{len(userName):<{HEADERSIZE}}".encode()
                
                user = {"Header" : userNameHeader , "Data" : userName}
                
                for clientSocket in clients:
                    if clientSocket != serverSocket:
                        clientSocket.send(user['Header'] + user['Data'] + msg['Header'] + msg['Data'])


# Listening to requests infinitely untill interupted
while True:
        # Accepting the user and storing its address in the below defined variables
        clientSocket, clientAddress = serverSocket.accept()
       
        # Getting the information user wants to send
        user = recieveMessage(clientSocket)
        if user is False:
            continue
        socketsList.append(clientSocket)
        clients[clientSocket] = user
        
        print(f"Connection from {clientAddress} has been established!! : UserName : {user['Data'].decode()}") 
            
        # We add some extra header information to our msg in order to know the size of the message we are sending
        # The message to be sent
        msg = "Welcome to the server,Thanks for connecting!!"
        # Adding the length of the message as the header information
        msg = f'{len(msg):<{HEADERSIZE}}' + msg
        
        # Sending information to client socket
        clientSocket.send(msg.encode())

        thread = threading.Thread(target = clientThread, args = (clientSocket,))
        thread.start()
        
        writeThread = threading.Thread(target = writeData)
        writeThread.start()
