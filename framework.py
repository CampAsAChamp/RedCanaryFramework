from datetime import datetime
import getpass
import json
import os
import socket
import subprocess
import unittest


# Helper class/data type for having all the Network info in one data structure to be able to pull parts of the data out
class NetworkData:
    def __init__(self, source_addr, source_port, dest_addr, dest_port, data_size, protocol):
        self.source_addr = source_addr
        self.source_port = source_port
        self.dest_addr = dest_addr
        self.dest_port = dest_port
        self.data_size = data_size
        self.protocol = protocol


# Helper class/data type for having all the process info in one data structure to be able to pull parts of the data out
class ProcessInfo:
    def __init__(self, process_name, process_cmd, process_id):
        self.process_name = process_name
        # The command name and list of arguments passed to it. Can strip the first part of this to be the process name
        self.process_cmd = process_cmd
        self.process_id = process_id


# Press Shift+F10 to execute it or replace it with your code.
class RCFramework:
    def __init__(self):
        # Each instance of the Framework will have its own log file
        self.m_logFile = open("log.json", "a")

    def __del__(self):
        self.m_logFile.close()

    # Start a process, given a path to an executable file and the desired (optional) command-line arguments
    # Do we want to wait for the process to finish or just to open it?
    def run_executable(self, path, command_args=[]):
        arg_list = [path]
        # Creates a list with [path and adds the optional command args to the list]
        # ex: ['/path/to/file' '-a' '-l']
        arg_list.extend(command_args)  # Will do nothing if there are no command-line arguments provided
        print(arg_list)
        # TODO: Look more into shell=True
        process = subprocess.Popen(args=arg_list, shell=True)
        print(arg_list[0], arg_list, process.pid)
        # pInfo = ProcessInfo(arg_list[0], arg_list, process.pid)
        # self.log_process_start()


    # Create a file of specified type at a specified location
    def create_file(self, path):
        # TODO: Sanitize the path before opening
        f = open(path, "w")
        f.close()
        # f.write("Hello World")

    # Modify a file
    # What does modify a file mean? Need clarification on that
    def modify_file(self, path):
        pass

    # Delete a file
    def delete_file(self, path):
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
    def send(self, host, port, data):
        # Try to connect to server, error if not able to connect
        # TODO: Make connect into a separate private function
        s = socket.socket()
        s.connect((host, port))

        # Send data to server
        # data = "Hello Server!"
        s.send(data.encode())

        # Receive data from server
        bufSize = 1024
        dataFromServer = s.recv(__bufsize=bufSize)

        # Print to console
        print(dataFromServer.decode())

        # Close the socket when done
        s.close()

    def log_process_start(self, p: ProcessInfo):
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

    def log_file_io(self, path, activityDesc, p: ProcessInfo):
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

    def log_network_activity(self, nd: NetworkData, p: ProcessInfo):
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


# If this were to be something I'd actually commit I would have actual unit tests with (hopefully) a testing framework
# Test Cases I am seeing
"""
- Check if file exists after calling create_file
- Check if file exists after calling create_file with same name as previous
- Calling create file on a path that does not exist (do we create the folders to get to that path?)
- Expected behavior of calling create_file with empty path
"""

def main():
    fw = RCFramework()

    cmd = "dir"
    cmdArgs = ["/d", "/w"]
    # fw.run_executable(cmd)  # Should run the regular dir command, no arguments
    fw.run_executable(cmd, cmdArgs)  # Should run the dir command with /d and /w --> "dir /d /w or dir /d/w"
    """   
    print("------------------------------")

    fileName = "test.txt"
    fw.create_file(fileName)  # Should create a file
    fw.modify_file(fileName)  # Should modify the file (currently does nothing)
    fw.delete_file(fileName)  # Should delete the file we just created
    fw.delete_file("asdf.txt")  # Should print error

    print("------------------------------")

    # Test out sending data to a source address and port
    # fw.send("127.0.0.1", 9090, "hello world")

    mockProcess = ProcessInfo("ls", "stuff", "23874")
    mockNetworkData = NetworkData("1.1.1.1", "8080", "8.8.8.8", "80", "1024", "HTTP")
    fw.log_process_start(mockProcess)
    fw.log_file_io("here/is/my/path", "create", mockProcess)
    fw.log_network_activity(mockNetworkData, mockProcess)

    print("------------------------------")
    
    """
    print("--End of main--\n")


# Press the green button in the gutter to run the script.
# Only runs if the file is being run as a script, not being imported as a module
if __name__ == '__main__':
    main()

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
