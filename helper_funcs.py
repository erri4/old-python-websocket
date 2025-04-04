import classes.User as User
from typing import Any


users = []
rooms = []


def getcliby(attr: str, con: Any):
    """
    gets a client location in the users list by an attribute.

    <code>attr: string: </code> the attribute to find the client by.<br>
    <code>con: any: </code> the content of the attribute.

    <code>return: integer | boolean: </code> the location of the client in the users list. false if it is not in the list.
    """
    global users
    for i in range(len(users)):
        if getattr(users[i], attr) == con:
            return i
    return False


def getroomby(attr: str, con: Any):
    """
    gets a room location in the rooms list by an attribute.

    <code>attr: string: the attribute to find the room by.<br>
    <code>con: any: </code> the content of the attribute.

    <code>return: integer | boolean: </code> the location of the room in the rooms list. false if it is not in the list.
    """
    global rooms
    for i in range(len(rooms)):
        if getattr(rooms[i], attr) == con:
            return i
    return False


def sendrooms(clobj: User.User) -> None:
    """
    send the rooms available to a given client.

    <code>clobj: User: </code> the user the rooms are sent to.

    <code>return: None. </code>
    """
    global rooms
    roms = []
    for i in range(len(rooms)):
        finroom = []
        for part in rooms[i].participants:
            if part.name in clobj.friends:
                finroom.append(part.name)
        roms.append([rooms[i].name, finroom, rooms[i].password != None])
    clobj.send(roms, 'rooms')


def sendparts(clobj: User.User) -> None:
    """
    send participants in the room for a given client.

    <code>clobj: User: </code> the user the participants are sent to.

    <code>return: None. </code>
    """
    global rooms
    rom = getroomby('name', clobj.room)
    parts = rooms[rom].participants
    re = []
    for p in parts:
        re.append([p.name, p.name in clobj.friends or p.name == clobj.name or p.loginmode == 2 or clobj.loginmode == 2, p == rooms[rom].host])
    clobj.send(re, 'rm_ppl')
