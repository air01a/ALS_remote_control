from multiprocessing.connection import Client
import time
import sys, getopt
import argparse


class CommandManager():
    def __init__(self, connector):
        self.connector = connector    
        self.COMMANDS={'start_session':self.basic_command,'stop_session':self.basic_command,'change_scan_folder':self.basic_command,'wait_queue_empty':self.wait_queue_empty_command}

    def basic_command(self, command):
        print("+ Executing %s" % command)
        self.connector.send(command)
        print(self.connector.recv())

    def wait_queue_empty_command(self,command):
        print("+ Waiting for empty queues")
        final = False
        while not final:
            self.connector.send('queues_empty()')
            res=self.connector.recv()
            if res[0]=='0':
                empty=res.split('=')[1]
                if (empty=='True'):
                    final = True
                else:
                    time.sleep(1)

    def command_exists(self, command):
        cmd = command.split('(')
        if cmd[0] in self.COMMANDS.keys():
            return True
        return False
    

    def manage_command(self,command):
        cmd = command.split('(')[0]
        if cmd in self.COMMANDS.keys():
            return self.COMMANDS[cmd](command)
        return "INEXISTENT COMMAND"


class ConnectionManager():
    HOST='localhost'
    PORT=13000

    def __init__(self):
        self.connected=False

    def change_port(self, port:int):
        self.PORT = port

    def change_host(self, host:str):
        self.HOST = host

    def connect(self):
        address = (self.HOST, self.PORT)
        try:
            self.conn = Client(address)
            self.connected=True
        except:
            self.connected=False
        return self.connected
    
    def recv(self):
        if not self.connected:
            return None
        
        return self.conn.recv()
    
    def send(self,data):
        self.conn.send(data)

    def close(self):
        self.conn.close()
    

def main():
    connection_manager = ConnectionManager()

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-H", "--host", help="Ip of the server to connect")
    argParser.add_argument("-p", "--port", type=int, help="Port of the server to connect")
    argParser.add_argument('commands', metavar='command', type=str, nargs='+',
                    help='commands to send in order')
    args = argParser.parse_args()
    if args.host!=None:
        connection_manager.change_host(args.host)
    
    if args.port!=None:
        connection_manager.change_port(args.port)
    

    command_manager =CommandManager(connection_manager)
    commands = args.commands
    for command in commands:
        if not command_manager.command_exists(command):
            print("Error : command %s does not exist" % command)
            sys.exit(-1)
    
    if not connection_manager.connect():
        print("Error : Can not connect to serveur %s:%i"%(connection_manager.HOST, connection_manager.PORT))
        sys.exit(-1)


    for command in commands:
        command_manager.manage_command(command)

    connection_manager.send('close')
    try:
        connection_manager.close()
    except:
        print("")

if __name__ == "__main__":
    main()

