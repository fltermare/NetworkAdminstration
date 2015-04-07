import re
import socket
import string
import subprocess
import time


host = "irc.twitch.tv"
port = 6667
roundtime = 10
#play_mode = 0

def log_write(log_list) :
    fp = open('./log_twitch', 'a', encoding = 'UTF-8')
    fp.write(str(log_list))
    fp.write('\n')
    fp.close()

def check_has_message(data) :
    return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data)

def mode_change(input) :
    if input == 'normal' :
        return 0
    elif input == 'democracy' :
        return 1
    elif input == 'violence' :
        return 2

#playmode doesn't be used now
def parse_command(data, speaker, playmode) :
    if speaker == username and re.match(r'^#chmod [normal|democracy|violence]', data):
        mode = re.findall("normal|democracy|violence", data)
        global play_mode
        play_mode = mode_change(mode[0])
        '''
        string = 'change mode to ' + str(mode)
        print(string)
        print(play_mode)
        '''
        return mode
    else :
        match = re.findall("a|b|up|down|right|left|start|select", data)
    return match



def key_press(inputs) :
    for input in inputs :
        for i in input :
            cmd = "xte 'str " + i +"' "
            subprocess.call([cmd], shell = True)

def democracy(command_buff) :
    global s
    i = 0
    voting_session = 10

    s.send(bytes("PRIVMSG #%s : -----here are the selections-----\r\n" %username, "UTF-8"))

    for cmds in command_buff :
        i += 1
        string = username + " : No." + str(i) + " "
        for cmd in cmds :
            string = string + cmd

        #print(string)
        s.send(bytes("PRIVMSG #%s\r\n" %string, "UTF-8"))

    s.send(bytes("PRIVMSG #%s : -----start voting-----\r\n" %username, "UTF-8"))
    s.send(bytes("PRIVMSG #%s : [bot] next round starts in 10 seconds\r\n" %username, "UTF-8"))
    voting_start = time.time()

    while True :
        now = time.time()
        if now - voting_start > voting_session :
            s.send(bytes("PRIVMSG #%s : -----vote end-----\r\n" %username, "UTF-8"))
            break

    #print("democracy")
    return

def violence(command_buff) :
    print("violence")
    return


def main() :
    username = input("Enter the account: ")
    key = input("Enter the key: ")
    global s
    s = socket.socket()
    s.connect((host, port))
    s.send(bytes("PASS %s\r\n" %key, "UTF-8"))
    s.send(bytes("NICK %s\r\n" %username, "UTF-8"))
    s.send(bytes("USER %s %s twitch :%s\r\n" %(username, host, username), "UTF-8"))
    s.send(bytes("JOIN #%s\r\n" %username, "UTF-8"))
    
    #mode 0 normal; mode 1 democracy; mode 2 violence
    global play_mode
    play_mode = 0

    command_buff = []
    game_start_time = time.time()
    #tmp_time = int(time.strftime('%S',time.localtime(time.time())))
    tmp_time = time.time()

    while True :
        #t = int(time.strftime('%S',time.localtime(time.time())))
        #print(t)

        #s.send(bytes("PRIVMSG #%s :Can you hear me?\r\n" %username, "UTF-8"))
        #print("sended")
        try :
            data = s.recv(1024).decode("UTF-8")
        except socket.error:
        #except :
            data = None            

        if check_has_message(data) :
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print(current_time)
            data = data.strip().split(':')
            
            #print("[Warning] this doesn't work when \':\' in the command")
            command = data[2]
            speaker = data[1].split('!')[0]

            list_buff = parse_command(command, speaker, play_mode)
            #command_buff = command_buff + list_buff
            command_buff.append(list_buff)
            print(command_buff)
            print(speaker)
            
            #log
            log_list = [play_mode, speaker, current_time, list_buff]
            log_write(log_list)
        
        t = time.time()
        if (t-tmp_time) > roundtime :
            print(t)

            if play_mode == 0 :
                key_press(command_buff)
                command_buff = []
            elif play_mode == 1 :
                democracy(command_buff)
                command_buff = []
            elif play_mode == 2 :
                violence(command_buff)
                command_buff = []

            tmp_time = t

            #s.send(bytes("PRIVMSG #%s : -----new round-----\r\n" %username, "UTF-8"))



if __name__ == "__main__" :
    main()