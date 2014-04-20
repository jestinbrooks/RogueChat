rooms = [
    {'name': "Foyer", 'description': "It looks like a Foyer. "},
    {'name': "Drawing Room", 'description': "It looks like a Drawing Room. "},
    {'name': "Dining Hall", 'description': "It looks like a Dining Hall. "}
]

names = ["Server", "server"]

help_text = """Rogue Chat is a roguelike chat room
Commands:
#enter <room name> : Moves you to the room you enter

#stab <name> : Kills the player you enter returning them to the lobby and
               making them choose a new name

#quit : Exits the client returning you to a terminal prompt

#look : Gives information for the room the player is in, a list of other
        rooms and a list of players in the room

#clean : Removes blood from the players current room and notifies occupants
         of that room

#hide body : Removes a body from the players current room and notifies the
             occupants of that room

#hang <description of art> : Adds a description of a piece of art to the
                             players current rooms description (must be
                             less than 20 characters in length)

#steal art : Removes any art from the wall of the players current room\n"""
