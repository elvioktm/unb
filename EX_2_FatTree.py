from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Intf
from mininet.node import Controller
from mininet.link import TCLink
import subprocess
import sys
from os import popen
import threading
import time

class POXBridge( Controller ):

    def start( self ):
        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd( self.pox, 'forwarding.l2_learning &' )
    def stop( self ):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )

controllers = { 'poxbridge': POXBridge }

class Switches( Node ):
    def config( self, **params ):
        super( Switches, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( Switches, self ).terminate()

def runNetwork():

    net = Mininet(topo=None, build=False,
                controller=POXBridge, link=TCLink)

    core = 4
    switch_type = 'ovsk'

    info('*** Adicona Super-Spines                             ***\n')
    info('----------------------\n')
    superspine = {}
    for x in range(0, core):
        superspine[x] = net.addSwitch('cr'+str(x) , switch=switch_type)


    info('*** Adiciona Spines                     ***\n')
    spine = {}
    for x in range(0,(core * 2)):
        spine[x] = net.addSwitch('ar'+str(x) , switch=switch_type )

    info('*** Adiciona Leafs                         ***\n' )
    leafs = {}
    for x in range(0, (core *2)):
        leafs[x] = net.addSwitch('er'+str(x) , switch=switch_type )



    info('*** Adiona links aos Super-Spine                      ***\n')
    for x in range(0,core*2, 2):
        net.addLink(superspine[0], spine[x], bw=10000)
        net.addLink(superspine[1], spine[x], bw=10000)
       
    for x in range(1, core*2, 2):
        net.addLink(superspine[2], spine[x], bw=10000)
        net.addLink(superspine[3], spine[x], bw=10000)
      
    info('*** Adiciona Links aos Spines                ***\n')
    for x in range(0, (core*2), 2):
        net.addLink(spine[x], leafs[x], bw=10000)
        net.addLink(spine[x], leafs[x+1], bw=10000)
        
    info('*** Adiciona Links aos leafs                ***\n')
    for x in range(1, (core*2), 2):
        net.addLink(spine[x], leafs[x], bw=10000)
        net.addLink(spine[x], leafs[x-1], bw=10000)
     

    net.build()


    #net.pingAll()
    CLI(net)
    net.stop()
    subprocess.call(['mn', '-c'])


if __name__ == '__main__':
    setLogLevel('info')
    runNetwork()
