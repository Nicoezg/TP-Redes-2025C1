class Rule:
    def __init__(self, data):
        self.ip_src = None
        self.ip_dst = None
        self.port_src = None
        self.port_dst = None
        self.protocol = None

        for key in self.__dict__:
            if key in data and data[key] is not None:
                setattr(self, key, data[key])

    def __str__(self):
        return str(self.__dict__)
