from twisted.words.protocol import irc
from hooks import Hooks
from twisted.internet import reactor, protocol, defer

class Tiger(IRCClient):
    def __init__(self, f):
        """Called with f argument as the factory :3"""
        self.hookEngine = f.controller.hooks.botHooks(self)
        self.nickname = f.mkNick()
        
    def signedOn(self):
        self.hookEngine(Hooks.signedOn)
        
    def irc_ERR_ERONEUSNICKNAME(self, prefix, params):
        if not self._registered:
            self.hookEngine(irc.ERR_ERRONEUSNICKNAME, self.nickname)
            self.factory.controller.killClient(self)
            
    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
        self._attemptedNick = self.factory.mkNick()
        self.hookEngine(irc.ERR_NICKNAMEINUSE, self.nickname, self._attemptedNick)
        self.setNick(self._attemptedNick)
        
class TigerFactory(protocol.ClientFactory):
    protocol = Tiger
    
    def __init__(self, controller):
        self.controller = controller
        self.defered = defer.Defered()
        self.deadDefered = defer.Defered()
        
    def buildProtocol(self, addr):
        client = self.protocol(self)
        
        self.defered.callback(client)
        
        return client
        
