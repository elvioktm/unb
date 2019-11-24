#!/usr/bin/python


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller , RemoteController,OVSSwitch

from optparse import OptionParser
from mininet.log import setLogLevel
from mininet.cli import CLI

class FatTree(Topo):
    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)
        self.args=None
        self.options=None
        self.parseArgs()
        self.TotalLink=0
        self.dpid=0

        self.Servers=[]
        self.SperSpine=[]
        self.Spine=[]
        self.Leafs=[]

        self.addLeafs()
        self.addSpines()
        self.addSuperSpines()
        self.addservers()
        self.addLinks()
       
    def addSuperSpines(self):
        k=self.options.kterm
        for x in range(0,(k/2)**2):
            self.SperSpine.append(self.addSwitch( 'C_S'+str(x),dpid='0001'+self.convertToDPIDformat() ))
            self.dpid+=1
        self.dpid=0
    
    def addSpines(self):
        k=self.options.kterm
        for x in range(0, k*k/2):
            self.Spine.append(self.addSwitch( 'A_S'+str(x),dpid='0002'+self.convertToDPIDformat() ))
            self.dpid+=1
        self.dpid=0
             
    def addLeafs(self):
        k=self.options.kterm
        for x in range(0, k*k/2):
            self.Leafs.append(self.addSwitch( 'E_S'+str(x),dpid='0003'+self.convertToDPIDformat()  ))
            self.dpid+=1
        self.dpid=0
 
    def addservers(self):
        k=self.options.kterm
        for x in range(0,(k**3)/4):
            self.Servers.append(self.addHost( 'H'+str(x) ))
     
    def addLinks(self):
        k=self.options.kterm  
        
    
        for x in range(0,k*k/2):
            for y in range(0,k/2):
                self.addLink( self.Leafs[x], self.Servers[y+(k/2)*x],y )

                self.TotalLink+=1
                
        for x in range(0,k):
            for y in range(0,k/2):
                for z in range(0,k/2):
              
                    self.addLink( self.Spine[y+(k/2)*x], self.Leafs[z+(k/2)*x],z,k/2+y )
                    self.TotalLink+=1
                  
                    self.addLink( self.SperSpine[z+(y*k/2)], self.Spine[x*(k/2)+y],x,k/2+z )
                    self.TotalLink+=1
                       
    def parseArgs( self ):
        opts = OptionParser()
        opts.add_option("--kterm",type='int' ,default=4, help="K term for FatTree Topology")
        (self.options, self.args) = opts.parse_args()       
     
    def convertToDPIDformat(self):
        paddTo12=''    
        temp=12-len(hex(self.dpid)[2:])
        for i in range(0,temp):
            paddTo12+= '0'
        return paddTo12+hex(self.dpid)[2:]
         


def simpleTest():

    topo = FatTree()
    hst=[]
    net = Mininet( topo=topo,switch=OVSSwitch, controller=lambda name: RemoteController( name, ip='127.0.0.1' ) )
    c0 = RemoteController( 'c0', ip='127.0.0.1' )
    net.start()
    c0.start()
    hosts=topo.Servers
    
    print "total links is: %s" %(topo.TotalLink) 
    
    for i in range(0,len(hosts)):
        hst.append(net.get('H'+str(i)))

    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()    
