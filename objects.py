
class Client:
    """ An object containing a clients name, location, and address """
    def __init__(self, add, sock):
        self.room = None
        self.name = ""
        self.description = "They look nondescript"
        self.address = add
        self.clientsock = sock


class Room:
    """ An object containing a list of room properties and methods for editing them"""
    def __init__(self, name, description):
        self.occupants_list = []
        self.name = name
        self.description = description
        self.bodies = 0
        self.poolofblood = False
        self.art = ""

    def get_description(self):
        full_description = self.description

        if self.bodies and not self.poolofblood:
            if self.bodies == 1:
                full_description += "There is 1 body on the floor. "
            else:
                full_description += "There are %s bodies on the floor. " % str(self.bodies)
        elif self.poolofblood and not self.bodies:
            full_description += "There is a pool of blood on the floor. "
        elif self.poolofblood and self.bodies:
            if self.bodies == 1:
                full_description += "There is 1 body in a pool of blood on the floor. "
            else:
                full_description += "There are %s bodies in a pool of blood on the floor. " % str(self.bodies)

        if self.art:
            full_description += "On the wall hangs " + self.art + ". "

        return full_description

    def stabbed(self, occupant):
        self.bodies += 1
        self.poolofblood = True
        self.occupants_list.remove(occupant)
