import socket


def receive(host, port):
    serverSocket = socket.socket()
    print("Created server socket")

    # Bind and listen
    serverSocket.bind((host, port))
    serverSocket.listen()
    print("Binding to %s:%s" % (host, port), "and listening...")

    # Accept connections
    while True:
        (clientConnected, clientAddress) = serverSocket.accept()
        print("Accepted a connection request from %s:%s" % (clientAddress[0], clientAddress[1]))

        bufferSize = 1024
        dataFromClient = clientConnected.recv(bufferSize)
        print("Data from client:", dataFromClient.decode())

        # Send some data back to the client
        # Have to convert to strings as send() doesn't take ints
        clientConnected.send(str(clientAddress[0]).encode())
        clientConnected.send(str(clientAddress[1]).encode())
        clientConnected.send("Hello Client!".encode())


# Run this script separately from the framework to be able to test the send() method
def main():
    address = "127.0.0.1"
    port = 9090
    receive(address, port)
    print("-- End of Server Main--")


# Press the green button in the gutter to run the script.
# Only runs if the file is being run as a script, not being imported as a module
if __name__ == '__main__':
    main()
