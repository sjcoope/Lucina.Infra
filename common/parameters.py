import utility

class Parameters:
    def __init__(self, configfile):
        self.configfile = configfile
        #TODO - Error handling of empty configfile string
        self.__loadConfig__(configfile)

    def __loadConfig__(self, configfile):
        with open(configfile, 'r') as myfile:
            self.data=myfile.read()

    def isValid(self):
        if not self.configfile:
            return False
        else:
            return True

    def __str__(self):
        return self.data