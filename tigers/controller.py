#!/usr/bin/env python
from tiger import TigerFactory, Tiger
from hooks import Hooks
from twisted.internet import ssl as sslx

class TigerController():
    factory = TigerFactory
    protocol = Tiger
    nickGenerator = None
    
    def __init__(self):
        self.clients = set()
        self.uniqueNicks = set()
        self.hooks = Hooks(self)
        self.connectors = set()
        
    def _buildFactory(self):
        return self.factory(self, self.protocol)
        
    def connectTiger(self, host, port, timeout = 30, bindAddress = None, ssl = False, defered = False):
        f = self._buildFactory()
        
        if ssl:
            connector = reactor.connectSSL(
                host, port, f, sslx.ClientContextFactory(), timeout = timeout, bindAddress = bindAddress
            )
        else:
            connector = reactor.connectTCP(host, port, f, timeout = timeout, bindAddress = bindAddress)
            
        self.connectors.add(connector)
        
        f.defered.addCallback(
            lambda client: self.connectors.discard(connector)    
        ).addCallback(
            lambda client: self.clients.add(client)
        )
        
        f.deadDefered.addCallback(
            lambda client: self.clients.discard(client)   
        ).addCallback(
            lambda client: self.connectors.discard(connector) # incase it didn't get removed by the onConnector.   
        )
        
        f.deadDefered.addCallback(self.lostTiger)
        
        return f
        
    def killClient(self, client):
        if hasattr(client, 'transport'):
            client.transport.loseConnection()
        if client.factory.connector:
            client.factory.connector.disconnect()
        
        client.factory.deadDefered.callback(client)
        