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

class Switches( Node ):
    
    def config( self, **params ):
        super( Switches, self).config( **params )

        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmd( 'sysctl net.ipv4.conf.all.proxy_arp=1' )


    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmd( 'sysctl net.ipv4.conf.all.proxy_arp=0' )
        super( Switches, self ).terminate()

class POXBridge( Controller ):

    def start( self ):
       
        self.pox = '%s/pox/pox.py' % os.environ[ 'HOME' ]
        self.cmd( self.pox, 'forwarding.l2_learning &' )
    def stop( self ):
        "Stop POX"
        self.cmd( 'kill %' + self.pox )

controllers = { 'poxbridge': POXBridge }

def runNetwork():

    net = Mininet(topo=None, build=False,
                controller=POXBridge, link=TCLink)


    start = 0
    num_cells = 5
    top_level_switches = 4
    bottom_level_servers = 1
    switch_type = 'ovsk'

    switches = {}
    info('*** Aciona os PODs                              ***\n')
    for x in range(0, num_cells):
        switches[x] = net.addSwitch('server' + str(x), switch = switch_type)
        for i in range(0, top_level_switches):
            name = 'sw' + str(x) +'_' + str(i)
            switches[name] = net.addSwitch(name, switch=switch_type)
            net.addLink(switches[x], switches[name], bw=10000)

    floor = 0
    for x in range(0, num_cells):
        for i in range(floor, top_level_switches):
            name1 = 'sw' + str(x) +'_' + str(i)
            name2 = 'sw' + str(i+1) +'_' + str(x)
            net.addLink(switches[name1], switches[name2], bw =1000)
        floor = floor +1



    net.build()



    CLI(net)
    net.stop()
    subprocess.call(['mn', '-c'])


if __name__ == '__main__':
        setLogLevel('info')
        runNetwork()
