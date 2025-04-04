from helper_funcs import getcliby, getroomby, sendrooms, sendparts, users, rooms
from classes.exceptions import UnrelatedException
from classes.Room import Room
import WebsocketServer as ws


REQUEST_HEADERS: dict[int, str] = {
                                    0: 'login',
                                    1: 'reg',
                                    2: 'create',
                                    3: 'join',
                                    4: 'col',
                                    5: 'leave',
                                    6: 'msg',
                                    7: 'move',
                                    8: 'eat',
                                    9: 'del',
                                    10: 'changep',
                                    11: 'addf',
                                    12: 'remf',
                                    13: 'sql',
                                    14: 'py',
                                    15: 'gue'
                                    }


def message_handler(client: ws.WebsocketServer.Client, msg, header: str):
    """
    handle the message.

    <code>client: Client:</code> the client who sent a message.<br>
    <code>msg: string | list | integer:</code> the message the client sent.<br>
    <code>header: string:</code> the header of the message the client sent.<br>
    valid headers:<br>
    - <code>login:</code> log in.
    - <code>reg:</code> register.
    - <code>create:</code> create a room.
    - <code>join:</code> join a room.
    - <code>col:</code> change the color.
    - <code>leave:</code> leave room.
    - <code>msg:</code> send message in the room.
    - <code>move:</code> move the avatar in the game.
    - <code>eat:</code> eat someone in the game.
    - <code>del:</code> delete the account.
    - <code>changep:</code> change the password.
    - <code>addf:</code> add a friend.
    - <code>remf:</code> remove a friend.
    - <code>sql:</code> admin feature. runs sql.
    - <code>py:</code> admin feature. runs python.

    <code>return: None.</code>
    """
    global users
    global rooms
    header = REQUEST_HEADERS[header]

    c = getcliby('client', client)
    obj = users[c]
    r = getroomby('name', obj.room)
    if header == 'gue':
        if obj.name != None:
            raise UnrelatedException()
        if msg[0] != 'admin':
            users[c].set_name_color(msg[0], msg[1])
            users[c].send(['name', True], 'success')
            users[c].send(msg[0], 'name')
            sendrooms(users[c])
            print(f'new client: {msg[0]}')
            users[c].send(0, 'xp')
            users[c].loginmode = 2
        else:
            users[c].send('username already exists', 'fail')
    elif header == 'create':
        if msg[0] == None:
            msg[0] = f"{obj.name}'s room"
        ex = getroomby('name', msg[0])
        if type(ex) == bool:
            ro = Room(str(msg[0]), obj, msg[1])
            rooms.append(ro)
            users[c].send('room', 'success')
            users[c].room = f'{msg[0]}'
            users[c].send(msg[0], 'rm_name')
            users[c].send([[obj.name, True, True]], 'rm_ppl')
            for cl in users:
                if cl.room == None and cl.name != None:
                    sendrooms(cl)
            ro.move()
            print(f'{obj.name} created room: {msg[0]}')
        else:
            users[c].send('room already exists', 'fail')
    elif header == 'join':
        rom = getroomby('name', msg[0])
        if type(rom) != bool:
            if users[c] not in rooms[rom].blacklist:
                if rooms[rom].password == None or msg[1] == rooms[rom].password:
                    rooms[rom].sysmsg(f'{obj.name} have joined the room')
                    rooms[rom].add_participant(users[c])
                    rooms[rom].move()
                    users[c].send(msg[0], 'rm_name')
                    users[c].send('room', 'success')
                    users[c].room = f'{msg[0]}'
                    for part in rooms[rom].participants:
                        sendparts(part)
                    print(f'{obj.name} joined room: {msg[0]}')
                else:
                    users[c].send('incorrect password', 'fail')
            else:
                users[c].send('you were banned from this room', 'fail')
    elif header == 'col':
        users[c].color = msg
        if type(r) != bool and r != None:
            rooms[r].move()
    elif header == 'leave':
        if type(r) == bool:
            raise UnrelatedException(1)
        rm = rooms[r].remove_participant(users[c])
        users[c].room = None
        rname = str(rooms[r].name)
        if rm == False:
            rooms[r].sysmsg(f'{obj.name} have left the room')
            rooms[r].move()
            for part in rooms[r].participants:
                sendparts(part)
        else:
            del rooms[r]
        for cl in users:
                if cl.room == None and cl.name != None:
                    sendrooms(cl)
        users[c].send('', 'rm_name')
        users[c].send('', 'rm_ppl')
        print(f'{obj.name} left room: {rname}')
    elif header == 'msg':
        if type(r) == bool:
            raise UnrelatedException(1)
        if msg[0] != '/':
            rooms[r].sendmsg(msg, users[c])
            print(f'{obj.name} sent {msg} in room {rooms[r].name}')
        else:
            if users[c] == rooms[r].host:
                l = msg.strip().split(' ')
                l[0] = l[0][1:]
                if len(l) >= 2:
                    if l[0] == 'kick' and l[1] != obj.name:
                        k = getcliby('name', l[1])
                        if type(k) != bool and users[k] in rooms[r].participants:
                            rooms[r].remove_participant(users[k])
                            users[k].room = None
                            users[k].send('you were kicked from the room', 'sys')
                            users[k].send('--disconnected from room--', 'sys')
                            rooms[r].sysmsg(f'{l[1]} was kicked from the room')
                            rooms[r].move()
                            for part in rooms[r].participants:
                                sendparts(part)
                            for cl in users:
                                    if cl.room == None and cl.name != None:
                                        sendrooms(cl)
                            users[k].send('', 'rm_name')
                            users[k].send('', 'rm_ppl')
                    elif l[0] == 'ban' and l[1] != obj.name:
                        k = getcliby('name', l[1])
                        if type(k) != bool and users[k] in rooms[r].participants:
                            rooms[r].remove_participant(users[k])
                            rooms[r].blacklist.append(users[k])
                            users[k].room = None
                            users[k].send('you were banned from the room', 'sys')
                            users[k].send('--disconnected from room--', 'sys')
                            rooms[r].sysmsg(f'{l[1]} was banned from the room')
                            rooms[r].move()
                            for part in rooms[r].participants:
                                sendparts(part)
                            for cl in users:
                                    if cl.room == None:
                                        sendrooms(cl)
                            users[k].send('', 'rm_name')
                            users[k].send('', 'rm_ppl')
                    elif l[0] == 'givehost':
                            k = getcliby('name', l[1])
                            if type(k) != bool:
                                rooms[r].host = users[k]
                                for part in rooms[r].participants:
                                    sendparts(part)
    elif header == 'move':
        users[c].move(msg[0], msg[1])
        rooms[r].move()
    elif header == 'eat':
        for part in rooms[r].participants:
            if obj.x < int(part.x) + 29 and obj.x > int(part.x) - 29:
                    if obj.y < int(part.y) + 29 and obj.y > int(part.y) - 29:
                        if part.client != client:
                            if obj.loginmode == 1:
                                sql = f"select xp from users where username='{obj.name}'"
                            xp = obj.xp
                            xp += 10
                            p = getcliby('client', part.client)
                            users[p].move(0, 0)
                            part.send('', 'uate')
                            users[c].send(xp, 'xp')
                            rep = [[obj.name, part.name], [[obj.color[0], obj.color[1], obj.color[2]], [part.color[0], part.color[1], part.color[2]]]]
                            rooms[r].sendall(rep, 'ate')
                            print(f'{obj.name} ate {part.name}')
        rooms[r].move()
    elif header == 'py' and obj.name == 'admin':
        try:
            output = eval(msg)
            users[c].send(str(output), 'pyres')
        except Exception as e:
            users[c].send(str(e), 'pyres')
    else:
        raise ValueError('invalid header')