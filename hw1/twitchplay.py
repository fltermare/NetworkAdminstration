import re
import socket
import string

host = "irc.twitch.tv"
port = 6667

def check_has_message(data):
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data)

def parse_message(self, data):
    return {
        'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
        'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
        'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
    }

def main() :
    username = input("Enter the account: ")
    key = input("Enter the key: ")
    s = socket.socket()
    s.connect((host, port))
    s.send(bytes("PASS %s\r\n" %key, "UTF-8"))
    s.send(bytes("NICK %s\r\n" %username, "UTF-8"))
    s.send(bytes("USER %s %s twitch :%s\r\n" %(username, host, username), "UTF-8"))
    s.send(bytes("JOIN #%s\r\n" %username, "UTF-8"))
    
    while True :
        #s.send(bytes("PRIVMSG #%s :Can you hear me?\r\n" %username, "UTF-8"))
        #print("sended")
        data = s.recv(1024).decode("UTF-8");
        if check_has_message(data) :
            data = data.strip().split(':')
            command = data[2]
            print(command)
            buff = data[1]
            speaker = buff.split('!')[0]
            print(speaker)



if __name__ == "__main__" :
    main()