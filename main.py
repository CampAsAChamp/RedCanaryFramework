from datetime import datetime
import getpass
import json
import os
import socket
import subprocess


# Helper class/data type for having all the Network info in one data structure
class NetworkData:
    def __init__(self, source_addr, source_port, dest_addr, dest_port, data_size, protocol):
        self.source_addr = source_addr
        self.source_port = source_port
        self.dest_addr = dest_addr
        self.dest_port = dest_port
        self.data_size = data_size
        self.protocol = protocol


# Helper class/data type for having all the process info in one data structure
class Process:
    def __init__(self, process_name, process_cmd, process_id):
        self.process_name = process_name
        self.process_cmd = process_cmd
        self.process_id = process_id


# Press Shift+F10 to execute it or replace it with your code.
class RCFramework:
    def __init__(self):
        self.m_logFile = open("log.json", "a")

    def __del__(self):
        self.m_logFile.close()

    # Start a process, given a path to an executable file and the desired (optional) command-line arguments
    @staticmethod
    def run_executable(path, command_args=[]):
        arg_list = [path]
        arg_list.extend(command_args)  # Will do nothing if there are no command-line arguments provided
        print(arg_list)
        subprocess.run(args=arg_list, shell=True)

    # Create a file of specified type at a specified location
    @staticmethod
    def create_file(path):
        f = open(path, "w")
        f.close()
        # f.write("Hello World")

    # Modify a file
    @staticmethod
    def modify_file(path):
        pass

    # Delete a file
    @staticmethod
    def delete_file(path):
        if os.path.exists(path):
            os.remove(path)
        else:
            print("The file does not exist:")
            print("\t" + path)

    # Establish a network connection and transmit data
    #  ! Needs a server running to accept the connection to be able to send data
    # ** For improvements on this, add a configurable amount of time to try to connect before timing out,
    #    instead of only trying once and throwing error if we can't connect on first try
    # ** Same for sending data
    # Make bufferSize configurable
    @staticmethod
    def send(host, port):
        # Try to connect to server, error if not able to connect
        s = socket.socket()
        s.connect((host, port))

        # Send data to server
        data = "Hello Server!"
        s.send(data.encode())

        # Receive data from server
        bufSize = 1024
        dataFromServer = s.recv(__bufsize=bufSize)

        # Print to console
        print(dataFromServer.decode())

        # Close the socket when done
        s.close()

    def log_process_start(self, p: Process):
        dict_log = {
            "timestamp": datetime.isoformat(datetime.now()),
            "username": getpass.getuser(),
            "process": {
                "name": p.process_name,
                "command_line": p.process_cmd,
                "id": p.process_id,
            }
        }
        jsonObj = json.dumps(dict_log)
        print(jsonObj)
        # String concat is slow and can be error-prone, so instead just write to the file twice
        self.m_logFile.write(jsonObj)
        self.m_logFile.write('\n')

    def log_file_io(self, path, activityDesc, p: Process):
        dict_log = {
            "timestamp": datetime.isoformat(datetime.now()),
            "path": path,
            "activity_desc": activityDesc,
            "username": getpass.getuser(),
            "process": {
                "name": p.process_name,
                "command_line": p.process_cmd,
                "id": p.process_id,
            }
        }
        jsonObj = json.dumps(dict_log)
        print(jsonObj)
        # String concat is slow and can be error-prone, so instead just write to the file twice
        self.m_logFile.write(jsonObj)
        self.m_logFile.write('\n')

    def log_network_activity(self, nd: NetworkData, p: Process):
        dict_log = {
            "timestamp": datetime.isoformat(datetime.now()),
            "username": getpass.getuser(),
            "network_data": {
                "source_addr": nd.source_addr,
                "source_port": nd.source_port,
                "dest_addr": nd.dest_addr,
                "dest_port": nd.dest_port,
                "data_size": nd.data_size,
                "protocol": nd.protocol
            },
            "process": {
                "name": p.process_name,
                "command_line": p.process_cmd,
                "id": p.process_id,
            }
        }
        jsonObj = json.dumps(dict_log)
        print(jsonObj)
        # String concat is slow and can be error-prone, so instead just write to the file twice
        self.m_logFile.write(jsonObj)
        self.m_logFile.write('\n')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    fw = RCFramework()
    # fw.run_executable("dir", ["/d"])
    # fw.run_executable("dir")
    fileName = "test.txt"
    fw.create_file(fileName)
    # fw.delete_file(fileName)
    # fw.delete_file("alskdfasldkfj")
    # fw.send("127.0.0.1", 9090)
    mockProcess = Process("ls", "stuff", "23874")
    mockNetworkData = NetworkData("1.1.1.1", "8080", "8.8.8.8", "80", "1024", "HTTP")
    fw.log_process_start(mockProcess)
    fw.log_file_io("here/is/my/path", "create", mockProcess)
    fw.log_network_activity(mockNetworkData, mockProcess)

    print("--End of main--\n")

"""
Start a process, given a path to an executable file and the desired (optional) command-line arguments
Use Python subprocess module
ex: framework.runExecutable(“path/to/file”, [“arg1, arg2”])

Create a file of specified type at a specified location
Use Python standard File I/O module
ex: framework.createFile(“path/to/file”)

Modify a file
ex: framework.modifyFile(“path/to/file”)

Delete a file
ex: framework.deleteFile(“path/to/file”)

Establish a network connection and transmit data
ex: framework.connect(host, port)
ex: framework.send(msg)

Additionally this program should keep a log of the activity it triggered.
The activity log allows us to correlate what data the test program generated with the actual data recorded by an EDR agent
This log should be in a machine friendly format (e.g CSV, TSV, JSON, YAML, etc)
Use JSON with the JSON module in Python for our functions
ex: framework.logProcessStart(...)
ex: framework.logFileCreation(...)
ex: framework.logNetworkActivity(...)
"""
