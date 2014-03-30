RogueChat
=========

A client and server for a roguelike chat room

If you are killed you must start over with a new name

Setup for running locally on a unix or linux computer

1. Check your version of python, I tested with 2.7.3 and 2.7.5 but it should work with any version of 2.6 or 2.7

2. Open terminal and enter python roguechatserver.py to start the server

3. Open a second terminal window and enter python roguechatclient.py to run the client

4. When asked for the host enter localhost

Commands

"#enter <roomname>" : Moves you to the room you enter

"#stab <name>" : Kills the player you enter returning them to the lobby and making them choose a new name

"#quit" : Exits the client returning you to a terminal prompt

"#look" : Gives information for the room the player is in, a list of other rooms and a list of players in the room

"#clean" : Removes blood from the players current room and notifies occupants of that room

"#hide body" : Removes a body from the players current room and notifies the occupants of that room


Thanks to binarytides.com for their tutorial on python sockets and example code that got this project started