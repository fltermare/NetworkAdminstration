import re
import socket
import string
import subprocess
import time


host = "irc.twitch.tv"
port = 6667
roundtime = 15
#play_mode = 0

def log_write(log_list) :
    fp = open('./log_twitch', 'a', encoding = 'UTF-8')
    fp.write(str(log_list))
    fp.write('\n')
    fp.close()

def log_mode(input) :
    fp = open('./log_twitch', 'a', encoding = 'UTF-8')
    fp.write('***mode change to ')
    fp.write(input)
    fp.write(' ***\n')
    fp.close()

def log_result(input) :
    fp = open('./log_twitch', 'a', encoding = 'UTF-8')
    fp.write(';;;result is ')
    fp.write(input)
    fp.write(' ;;;\n')
    fp.close()    

def check_has_message(data, n) :
    if n == 0 :
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data)
    elif n == 1 :
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :[0-9]+', data)


def mode_change(input) :
    global s
    if input == 'normal' :
        s.send(bytes("PRIVMSG #%s : ****mode change to normal****\r\n" %username, "UTF-8"))
        log_mode(input)
        return 0
    elif input == 'democracy' :
        s.send(bytes("PRIVMSG #%s : ****mode change to democracy****\r\n" %username, "UTF-8"))
        log_mode(input)
        return 1
    elif input == 'violence' :
        s.send(bytes("PRIVMSG #%s : ****mode change to violence****\r\n" %username, "UTF-8"))
        log_mode(input)
        return 2

#playmode doesn't be used now
def parse_command(data, speaker, playmode) :
    if speaker == username and re.match(r'^#chmod [normal|democracy|violence]', data):
        mode = re.findall("normal|democracy|violence", data)
        global play_mode
        play_mode = mode_change(mode[0])
        return []
    else :
        match = re.findall("a|b|up|down|right|left|start|select", data)
    return match


def key_press(inputs) :
    for input in inputs :
        for i in input :
            if re.match(r'[EOC]', i): 
                continue
            elif re.match(r'[a]', i) :
                cmd = "xte 'keydown End' 'usleep 70000' 'keyup End'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[b]', i) :
                cmd = "xte 'keydown Page_Up' 'usleep 70000' 'keyup Page_Up'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[up]', i):
                cmd = "xte 'keydown Up' 'usleep 70000' 'keyup Up'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[down]', i) :
                cmd = "xte 'keydown Down' 'usleep 70000' 'keyup Down'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[right]', i) :
                cmd = "xte 'keydown Right' 'usleep 70000' 'keyup Right'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[left]', i) :
                cmd = "xte 'keydown Left' 'usleep 70000' 'keyup Left'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[start]', i) :
                cmd = "xte 'keydown Return' 'usleep 70000' 'keyup Return'"
                subprocess.call([cmd], shell = True)
            elif re.match(r'[select]', i) :
                cmd = "xte 'keydown BackSpace' 'usleep 70000' 'keyup BackSpace'"
                subprocess.call([cmd], shell = True)
'''                    
            cmd = "xte 'str " + i +"' "
            subprocess.call([cmd], shell = True)
'''


def democracy(command_buff) :
    global s
    i = 0
    voting_session = 15
    if command_buff == [] : return

    s.send(bytes("PRIVMSG #%s : -----here are the selections-----\r\n" %username, "UTF-8"))
    cmds = list(set(command_buff))
    if 'EOC' in command_buff :
        cmds.remove('EOC')

    string = username + " : "
    for cmd in cmds :
        string = string + cmd + " "
    s.send(bytes("PRIVMSG #%s\r\n" %string, "UTF-8"))
    print(cmds)

    s.send(bytes("PRIVMSG #%s : -----start voting-----\r\n" %username, "UTF-8"))
    s.send(bytes("PRIVMSG #%s : [bot] next round starts in 15 seconds\r\n" %username, "UTF-8"))
    voting_start = time.time()

    vote_dict = dict()
    while True :
        try :
            time.sleep(0.1)            
            vdata = s.recv(1024).decode("UTF-8")
        except socket.error :
            vdata = None

        if check_has_message(vdata, 0) :
            vdata = vdata.strip().split(':')
            if len(vdata) != 3 : break
            ballots = parse_command(vdata[2], "voting", play_mode)
            print(ballots)
            for ballot in ballots :
                if ballot in cmds :
                    vote_dict[ballot] = vote_dict.get(ballot, 0) + 1

        now = time.time()
        if now - voting_start > voting_session :            
            s.send(bytes("PRIVMSG #%s : -----vote end next round starts-----\r\n" %username, "UTF-8"))
            
            tmp = list()
            for key, value in vote_dict.items() :
                tmp.append((value, key))
            tmp = sorted(tmp, reverse=True)
            print(tmp)
            tmp2 = [(key, value) for (key, value) in tmp if key == tmp[0][0]]
            if len(tmp2) == 1 :
                s.send(bytes("PRIVMSG #channal : -----result %s-----\r\n" %tmp2[0][1], "UTF-8"))
                key_press([[tmp2[0][1]]])
                log_result(tmp2[0][1])
                print(tmp2[0][1])
            else :
                tmp3 = [value for (key, value) in tmp2]
                democracy(tmp3)

            time.sleep(0.5)
            break

    return


def violence(command_buff) :
    global s
    voting_session = 15
    command_dict = dict()
    top = command_buff[0]
    last = 0
    for cmd in command_buff:
        if cmd == top :
            last += 1
        else :
            command_dict[top] = command_dict.get(top, 0)
            if command_dict[top] < last :
                command_dict[top] = last
            last = 1
            top = cmd
    command_dict['EOC'] = 0

    tmp = list()
    for key, value in command_dict.items() :
        tmp.append((value, key))

    tmp = sorted(tmp, reverse=True)
    print(tmp)
    tmp2 = [(key, value) for (key, value) in tmp if key == tmp[0][0]]
    if len(tmp2) == 1 :
        s.send(bytes("PRIVMSG #channal : -----result %s-----\r\n" %tmp2[0][1], "UTF-8"))
        key_press([[tmp2[0][1]]])
        log_result(tmp2[0][1])
        print(tmp2[0][1])
    else :
        tmp3 = [value for (key, value) in tmp2]
        democracy(tmp3)
        print("tmp3")
        print(tmp3)
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
    tmp_time = time.time()

    while True :

        #s.send(bytes("PRIVMSG #%s :Can you hear me?\r\n" %username, "UTF-8"))
        #print("sended")
        try :
            data = s.recv(1024).decode("UTF-8")
        except socket.error:
        #except :
            data = None            

        if check_has_message(data, 0) :
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print(current_time)
            data = data.strip().split(':')
            
            #print("[Warning] this doesn't work when \':\' in the command")
            command = data[2]
            speaker = data[1].split('!')[0]

            list_buff = parse_command(command, speaker, play_mode)
            list_buff.append('EOC')
            command_buff = command_buff + list_buff
            #command_buff.append(list_buff)
            print(command_buff)
            print(speaker)
            
            #log
            log_list = [play_mode, speaker, current_time, list_buff]
            log_write(log_list)
        
        t = time.time()
        if (t-tmp_time) > roundtime :
            #print(t)

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