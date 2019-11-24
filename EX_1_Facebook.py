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

class switches( Node ):

    def config( self, **params ):
        super( switches, self).config( **params )

        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmd( 'sysctl net.ipv4.conf.all.proxy_arp=1' )


    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmd( 'sysctl net.ipv4.conf.all.proxy_arp=0' )
        super( switches, self ).terminate()

class POXBridge( Controller ):

    def start( self ):

        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd( self.pox, 'forwarding.l2_learning &' )
    def stop( self ):

        self.cmd( 'kill %' + self.pox )

controllers = { 'poxbridge': POXBridge }

def runNetwork():

    net = Mininet(topo=None, build=False,
                controller=POXBridge, link=TCLink)


    spine = 4
    leafs = 48

    switch_type = 'ovsk'

    switches = {}
    info('*** Adciona os Switches Superspines                          ***\n')
    for x in range(0, spine):
        switches[x] = net.addSwitch('cr' + str(x), switch = switch_type)
    for x in range(0, leafs):
        switches[x+spine] = net.addSwitch('er' + str(x), switch = switch_type)


    for x in range(0, spine):
    
        for i in range(0, leafs):
          

            net.addLink(switches[x], switches[i+spine], bw =100000)

    net.build()



    CLI(net)
    net.stop()
    subprocess.call(['mn', '-c'])


if __name__ == '__main__':
        setLogLevel('info')
        runNetwork()
