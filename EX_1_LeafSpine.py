#!/usr/bin/python

'''
#### Opcoes
    --version                        show program's version number and exit
    -h, --help                       show this help message and exit
    -l INTEGER, --leaves=INTEGER     specify the number of leaf switches
    -s INTEGER, --spines=INTEGER     specify the number of spine switches
    -c IP, --controller=IP           specify the IP address of the controller
    -v, --verbose                    display additional logging information

A opcao do controlador (`` -c``` ou `` --controller```) pode ser especificada varias vezes
para especificar controladores adicionais aos quais um Switche se conectara.

O primeiro controlador especificado sera usado como o controlador primario.

#### Executando
Inicie o script executando `` `sudo python spine_leaf.py [options]` ``

Apos executar o script e se um controlador foi especificado, voce pode
verificar se todos os switches estao registrados no controlador e todas as
conexoes (links) estao disponiveis.

- Os prefixos dos Spines sao `` `S1```
- Os prefixos dos Leafs sao `` `L2```

Apos verificar se os switches estao registrados no controlador,
voce pode emitir um comando `` pingall``` no console `` mininet``` para descobrir
os hosts atraves do ARP. A interface do usuario do controlador para ver os hosts


Exemplo de uso: sudo python spine_leaf.py <n?mero_do_switches_do_spine> <numero_de_switches_leaf>> <IP_controller_primario_IP> <IP_controller_secondario>
sudo python spine_leaf.py 2 4 172.17.0.1 172.17.0.2

Tambem e possivel configurar o link Largura de banda, atraso, perda, tamanho maximo da fila_size para os
links da arquitetura Spine Leaf e conexoes dos serviores para os leafs alterando as variaveis globais
link_spine_leaf e link_host_leaf no script.

O padrao e: Largura de banda = 10000, Atraso = 1 ms, Perda = 0, Tamanho maximo da fila = 1000000

'''

from optparse import OptionParser
import os
import sys
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import OVSSwitch, Controller, RemoteController


spineList = [ ]
leafList = [ ]
switchList = [ ]

link1 = dict(bw=10000, delay='1ms', loss=0, max_queue_size=1000000, use_htb=True)
link2 = dict(bw=15, delay='2ms', loss=0, max_queue_size=1000, use_htb=True)
link3 = dict(bw=10, delay='5ms', loss=0, max_queue_size=1000, use_htb=True)
link4 = dict(bw=5, delay='10ms', loss=0, max_queue_size=500, use_htb=True)
link5 = dict(bw=1, delay='15ms', loss=0, max_queue_size=100, use_htb=True)

link_spine_leaf = link1
link_host_leaf = link1



class dcSpineLeafTopo(Topo):
    "arquitetura linear onde k switches."

    def __init__(self, k, l, **opts):
        """Init.
            k: numero de  switches (and hosts)
            hconf: opcoes de configuracao dos servers 
            lconf: opcoes de configuracao dos links"""

        super(dcSpineLeafTopo, self).__init__(**opts)

        self.k = k
        self.l = l

        for i in irange(0, k-1):
            spineSwitch = self.addSwitch('s%s%s' % (1,i+1))
            spineList.append(spineSwitch)

        for i in irange(0, l-1):
            leafSwitch = self.addSwitch('l%s%s' % (2, i+1))

            leafList.append(leafSwitch)
            host1 = self.addHost('h%s' % (i+1))
            #host12 = self.addHost('h%s' % (i+1))
            #hosts1 = [ net.addHost( 'h%d' % n ) for n in 3, 4 ]

           
            self.addLink(host1, leafSwitch, **link_host_leaf)
            #self.addLink(host12, leafSwitch)

        for i in irange(0, k-1):
            for j in irange(0, l-1): #this is to go through the leaf switches
                self.addLink(spineList[i], leafList[j], **link_spine_leaf)

def simpleTest(options):

    controllers = None
    if options.controllers:
        controllers = []

        for idx, addr in enumerate(options.controllers):
            controllers.append(RemoteController( "c%d" % idx, ip=addr))

    class MultiSwitch( OVSSwitch ):

    def start( self, controllers ):
        return OVSSwitch.start( self, [ cmap[ self.name ] ] )

    topo = dcSpineLeafTopo(k=options.spine_count, l=options.leaf_count)
    switchList = spineList + leafList
    net = Mininet(  topo=topo, switch=MultiSwitch, build=False, link=TCLink )

    if controllers:
        names = str([c.name for c in controllers]).replace("'", "")
        print "Conecta todos os swiches ao controlador"
        cString = "{"
        for i in irange(0, len(switchList)-1):
            if i != len(switchList)-1:
                tempCString = "'%s' : %s," % (switchList[i], names)
            else:
                tempCString = "'%s' : %s" % (switchList[i], names)
            cString += tempCString
        cmapString = cString + "}"
        cmap = cmapString

    for c in controllers or []:
        net.addController(c)

    net.build()

    for c in controllers or []:
        c.start()

    net.start()
    print "Conexoes dos servers"
    dumpNodeConnections(net.hosts)

    CLI( net )
    net.stop()

if __name__ == '__main__':
    parser = OptionParser(version="%prog 1.0")
    parser.add_option("-l", "--leaves", dest="leaf_count",
        help="Especifica o numero de swiches Leafs",
        metavar="INTEGER", type="int", default=4)
    parser.add_option("-s", "--spines", dest="spine_count",
        help="Especifica o numero de swiches Spines",
    	metavar="INTEGER", type="int", default=2)
    parser.add_option("-c", "--controller", dest="controllers",
        help="Especifica o Ip do controlador",
        action="append", metavar="IP")
    parser.add_option("-v", "--verbose", dest="verbose",
		help="Exibe informacoes adicionais de registro",
		action="store_true", default=False)

    (options, args) = parser.parse_args()

    if options.verbose:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    simpleTest(options)
