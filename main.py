from datetime import datetime
import getpass
import json
import os
import socket
import subprocess


# Press Shift+F10 to execute it or replace it with your code.
class RCFramework:
    # Member Variable for the log
    m_logFile = open("log.json", "a")

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
        f.write("Hello World")

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
    @staticmethod
    def send(host, port):
        # Try to connect to server
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

    def log_process_start(self, process_name, process_command_line, process_id):
        dict_log = {
            "timestamp": datetime.isoformat(datetime.now()),
            "username": getpass.getuser(),
            "process": {
                "name": process_name,
                "command_line": process_command_line,
                "id": process_id,
            }
        }
        jsonObj = json.dumps(dict_log)
        print(jsonObj)
        # String concat is slow, so instead just write to the file twice
        self.m_logFile.write(jsonObj)
        self.m_logFile.write('\n')

        """
        if log file already exists
            open log file
            add json to the end
        else
            create new log file
        """

    def log_file_creation(self):
        pass

    def log_network_activity(self):
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    fw = RCFramework()
    # fw.run_executable("dir", ["/d"])
    # fw.run_executable("dir")
    # fileName = "test.txt"
    # fw.create_file(fileName)
    # fw.delete_file(fileName)
    # fw.delete_file("alskdfasldkfj")
    # fw.send("127.0.0.1", 9090)
    fw.log_process_start("ls", "stuff", 23874)

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
