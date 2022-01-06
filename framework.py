from datetime import datetime
import getpass
import json
import os
import psutil  # Needs to be downloaded from Pip
import socket
import subprocess
import sys


# -------
# Not familiar with Python in large codebases/companies so I'm unsure what the standard ways of doing documentation are. This is what I found online
# ---------

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


class RCFramework:
    """
    A framework that will generate endpoint activity. We will be able to test an EDR agent and ensure it generates
    the appropriate telemetry

    Attributes
    ----------
    m_logFile: file
        A file for logging all the activity the framework has triggered. It will
        allow us to correlate what data the test program generated with the actual data recorded by an EDR agent
    """

    def __init__(self):
        # Each instance of the Framework will have its own log file
        # Open it in appending mode, won't overwrite the file if it already exists, just appends to the end
        self.m_logFile = open("log.json", "a")

    def __del__(self):
        self.m_logFile.close()

    """
        run_executable(path, command_args=[])
            - Start a process, given a path to an executable file and the desired (optional) command-line arguments
            - [Question]: Do we want to wait for the process to finish or just to open it?
            - [Improvement]: Sanitize the path before opening (Check if path exists, check slashes are the correct way,...etc)
            - [Requirement]: Path is a file path to an existing file
            
            path: str
                Path to the executable/command to be executed
            command_args: list[string]
                Optional list of command arguments to the executable/command to be executed
    """

    def run_executable(self, path, command_args=[], useShell: bool = False):
        # Creates a list with path and adds the optional command args to the list
        # ex: ['/path/to/file' '-a' '-l']
        arg_list = [path]
        arg_list.extend(command_args)  # Will do nothing if there are no command-line arguments provided
        # Setting the shell argument to a true value causes subprocess to spawn an intermediate shell process, and tell it to run the command
        process = subprocess.Popen(args=arg_list, shell=useShell)

        name, cmd = self.__getProcessUtilInfo(process.pid)

        # *! Improvements: I might separate variable for pInfo and just create one inside the log_process_start()
        # function call, as we don't need to do anything with pInfo after this.
        # Converting to string since we aren't doing any calculations with the pid, and want to keep consistent with everything else
        pInfo = ProcessInfo(name, cmd, str(process.pid))
        self.log_process_start(pInfo)


    def __getProcessUtilInfo(self, pid):
        processUtilInfo = psutil.Process(pid)
        name = processUtilInfo.name()
        cmd = " ".join(processUtilInfo.cmdline())
        return name,cmd

    """
        create_file(path)
            - Create a file of specified type at a specified location
            - [Improvement]: Sanitize the path before opening (Check if path exists, check slashes are the correct way,...etc)                -
            - [Requirement]: Path is a file path to an existing file   
    
            path: str
                Path to the file to be created
    """

    def create_file(self, path):
        # Open file in overwrite mode, if the file already exists overwrite it
        fileOpenMode = "w"
        f = open(path, fileOpenMode)
        f.close()

        # A little unsure of what to be putting for here
        pid = os.getpid()
        name, cmd = self.__getProcessUtilInfo(pid)

        p = ProcessInfo(name, cmd, str(pid))
        activityDesc = "Create"
        self.log_file_io(path, activityDesc, p)

    """
        modify_file(path)
            - Modify a file
            - [Question]: What does modify a file mean?
            - [Requirement]: Path is a file path to an existing file
            
            path: str
                Path to the file to be modified
    """

    def modify_file(self, path):
        # Open it in appending mode, as we are appending. It won't overwrite the file if it already exists, just appends to the end
        fileOpenMode = "a"
        f = open(path, fileOpenMode)
        f.close()

        # A little unsure of what to be putting for here
        pid = os.getpid()
        name, cmd = self.__getProcessUtilInfo(pid)
        p = ProcessInfo(name, cmd, str(pid))
        activityDesc = "Modify"
        self.log_file_io(path, activityDesc, p)

    """
        delete_file(path)
            - Delete a file
            - [Question]: Should we still log if the file isn't there?
            
            path: str
                Path to the file to be deleted
    """

    def delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)

            # A little unsure of what to be putting for here
            pid = os.getpid()
            name, cmd = self.__getProcessUtilInfo(pid)
            p = ProcessInfo(name, cmd, str(pid))
            activityDesc = "Delete"
            self.log_file_io(path, activityDesc, p)
        else:
            print("The file does not exist:")
            print("\t" + path)

    """
        send(host, port, data)
            - Establish a network connection and transmit data
            - [Requirement]: Needs a server running on (host:port), to accept the connection and be able to send data
            - [Requirement]: socket.send() can only be used with a connected socket, which means it can only be used with TCP based sockets, not UDP
            - [Requirement]: Data sent through socket.send() needs to be in bytes format. Convert from a string using encode()
            - [Improvement]: Add a configurable amount of time to try to connect before timing out, instead of only trying once and throwing error if we can't connect on first try.
            - [Improvement]: Make connect into a separate private function
            - [Improvement]: Same for the call to actually send the data
            - [Improvement]: Make bufferSize configurable
    
            host: str
                Destination address to transmit data
            port: str
                Port to transmit data
            data: str
                String to be sent to the host & port, will be converted to bytes
    """

    def send(self, host, port, data):
        #   Try to connect to server, error if not able to connect

        # Create a client socket
        clientSocket = socket.socket()

        # Connect to the server
        clientSocket.connect((host, port))

        # Send data to server
        clientSocket.send(data.encode())
        dataSentSize = str(sys.getsizeof(data))
        protocol = "TCP"

        # Receive sourceAddr and sourcePort from server
        bufferSize = 1024
        sourceAddr = clientSocket.recv(bufferSize).decode()
        sourcePort = clientSocket.recv(bufferSize).decode()

        # Close the socket when done
        clientSocket.close()

        # For logging
        pid = os.getpid()
        name, cmd = self.__getProcessUtilInfo(pid)
        p = ProcessInfo(name, cmd, str(pid))
        nd = NetworkData(sourceAddr, sourcePort, host, str(port), dataSentSize, protocol)
        self.log_network_activity(nd, p)

    """
        __log_to_file(p: ProcessInfo, d: dict = {})
            - Private helper function which does the actual logging to the json file.
            - The rest of the log functions are wrappers around this function.
            - Creates a Python dictionary which mimics JSON to output
            - All of the different log-types have common stuff which they all have to log (timestamp, username, process info)
            - Adds the log-type specific info in addition to this common dictionary, converts the whole thing to JSON, and append this JSON to the log file
    
            d: dict = []
                Log-type specific logging info
            p: ProcessInfo
                Information about the process to log
    """

    def __log_to_file(self, p: ProcessInfo, d: dict = {}):
        commonLogDict = {
            "timestamp": datetime.isoformat(datetime.now()),
            "username": getpass.getuser(),
            "process": {
                "name": p.process_name,
                "command_line": p.process_cmd,
                "id": p.process_id,
            }
        }
        commonLogDict.update(d)
        jsonObj = json.dumps(commonLogDict)

        # String concat is slow and can be error-prone, so instead just write to the file twice
        self.m_logFile.write(jsonObj)
        self.m_logFile.write('\n')

    """
        log_process_start(p: ProcessInfo)
            p: ProcessInfo
                Information about the process to log
    """

    def log_process_start(self, p: ProcessInfo):
        self.__log_to_file(p)

    """    
        log_file_io(path, activityDesc, p: ProcessInfo)
            path: str
                Path to the file which was created/modified/deleted
            activityDesc: str
                Type of activity which was performed on the file [created/modified/deleted]
            p: ProcessInfo
                Information about the process to log
    """

    def log_file_io(self, path, activityDesc, p: ProcessInfo):
        dict_log = {
            "path": path,
            "activity_desc": activityDesc,
        }
        self.__log_to_file(p, dict_log)

    """
        log_network_activity(nd: NetworkData, p: ProcessInfo)
            nd: NetworkData
                Information about the network for which we sent data to
            p: ProcessInfo
                Information about the process to log
    """

    def log_network_activity(self, nd: NetworkData, p: ProcessInfo):
        dict_log = {
            "network_data": {
                "source_addr": nd.source_addr,
                "source_port": nd.source_port,
                "dest_addr": nd.dest_addr,
                "dest_port": nd.dest_port,
                "data_size": nd.data_size,
                "protocol": nd.protocol
            }
        }
        self.__log_to_file(p, dict_log)


# If this were to be something I'd actually commit I would have actual unit tests with (hopefully) a testing framework
# -- Some test Cases I am seeing: --
"""
- Check if file exists after calling create_file
- Verify behavior of calling create_file on an already existing file
- Calling create file on a path that does not exist (do we create the folders to get to that path?)
- Expected behavior of calling create_file with empty path
- Sending nothing/empty data
- Attempt to send data to server that isn't running
- Attempt to send data to server on different port than server is running on
- Creating the log file if the file doesn't exist yet
- Verify logs are getting appended to existing file
- Test all three log functions and make sure they are logging their correct stuff and not one of the others
"""


def main():
    fw = RCFramework()

    # Some manual tests and examples of the framework
    # Windows
    if os.name == "nt":
        cmd = "dir"
        cmdArgs = ["/d", "/w"]
        useShell = True
    elif os.name == "posix":
        cmd = "ls"
        cmdArgs = ["-l", "-a"]
        useShell = False

    fw.run_executable(cmd, useShell=useShell)  # Should run the regular dir command, no arguments
    fw.run_executable(cmd, cmdArgs, useShell)  # Should run the dir command with /d and /w --> "dir /d /w or dir /d/w"
    print("------------------------------")

    fileName = "test.txt"
    fw.create_file(fileName)  # Should create a file
    fw.modify_file(fileName)  # Should modify the file (currently does nothing)
    fw.delete_file(fileName)  # Should delete the file we just created
    fw.delete_file("asdf.txt")  # Should print error that file does not exist

    print("------------------------------")
    # Test out sending data to a source address and port (same address and port that the server is listening for)
    address = "127.0.0.1"
    port = 9090
    fw.send(address, port, "hello world")

    mockProcess = ProcessInfo("ls", "stuff", "23874")
    mockNetworkData = NetworkData("1.1.1.1", "8080", "8.8.8.8", "80", "1024", "HTTP")
    fw.log_process_start(mockProcess)
    fw.log_file_io("here/is/my/path", "create", mockProcess)
    fw.log_network_activity(mockNetworkData, mockProcess)

    print("------------------------------")
    print("--End of main--\n")


# Only runs if the file is being run as a script, not being imported as a module
if __name__ == '__main__':
    main()
