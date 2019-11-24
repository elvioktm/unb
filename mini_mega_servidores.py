# Estudo comparativo de desempenho de infra-estrutura de arquiteturas de rede intra-data center
# Dissertacao apresentada como requisito para conclusao do Mestrado Profissional em Computacao Aplicada PPCA UNB - DF
#
# ARQUITETURAS DCN Leaf-Spine, Fat-tree, Hybrid Fat-tree, Facebook 4-post e Facebook New Fabric
#
#AUTOR: Elvio de Sousa  e-mail: elvio@elvio.net.br
# Criado em 17 10 2019

# Este programa e um software livre; voce pode redistribui-lo e / ou modificar
# nos termos da Licenca Publica Geral GNU versao 2 como
# publicado pela Free Software Foundation;
#
# Este programa e distribuido na esperanca de que seja util,
# mas SEM QUALQUER GARANTIA; sem sequer a garantia implicita de
# COMERCIABILIDADE ou ADEQUACAO A UM OBJETIVO ESPECIFICO. Veja o
# GNU General Public License para mais detalhes.
#

"""
# Os comandos abaixo devem ser usados para executar o controlador: 
# use um terminal para o controlador. O comando abaixo executa o controlador. 
 
 ./pox.py forwarding.l2_pairs openflow.discovery misc.full_payload openflow.of_01 --port=6653

# use outro terminal para fazer executar a topologia  e dependedo do tamanho e da escala aguarde....

 sudo python *nome do arquivo*
 
# Abra outro terminal e execute topologias que tambem possui testes de iperf e ping 

sudo python iperf_ping.py 

# quando for escalar as topologias abra outro terminal e execute o mini_mega_servidores.py que cont?m o codigo para escalar mais hosts nos switches executar os testes

mini_mega_servidores.py

# Nossos testes foram executados para medir atrazo e largura de banda das arquiteturas Leaf-Spine, Fat-tree, Hybrid Fat-tree, Facebook 4-post e Facebook New Fabric

Para alterar a toplogia que o programa vai executar deve mudar seguinte linha: 

topo = {}(n=4)

coforme exemplo topo = {LeafSpine}(n=4) onde n e o numero de niveis ou hierarquias dos PODs (Super-spine Spine e Leaf)

{LeafSpine, Fattree, HybridFattree, Facebook4post e FacebookNewFabric}

Para finalizar um processo mininet executando em segundo plano, execute o comando:

sudo mn -c

"""

#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.node import Controller
from mininet.cli import CLI
import os
import time
import thread
from time import time, sleep
from select import poll, POLLIN
from subprocess import Popen, PIPE


def iperf_thread(net, src, dst):
    host_pair = [src, dst]
    bandwidth = net.iperf(host_pair, seconds = 100)

def monitorFiles( outfiles, seconds, timeoutms ):
    devnull = open( '/dev/null', 'w' )
    tails, fdToFile, fdToHost = {}, {}, {}
    for h, outfile in outfiles.iteritems():
        tail = Popen( [ 'tail', '-f', outfile ],
                      stdout=PIPE, stderr=devnull )
        fd = tail.stdout.fileno()
        tails[ h ] = tail
        fdToFile[ fd ] = tail.stdout
        fdToHost[ fd ] = h

    readable = poll()
    for t in tails.values():
        readable.register( t.stdout.fileno(), POLLIN )
    # Executa at? o tempo e numero definido
    endTime = time() + seconds
    while time() < endTime:
        fdlist = readable.poll(timeoutms)
        if fdlist:
            for fd, _flags in fdlist:
                f = fdToFile[ fd ]
                host = fdToHost[ fd ]
                # Wait for a line of output
                line = f.readline().strip()
                yield host, line
        else:

            yield None, ''
    for t in tails.values():
        t.terminate()
    devnull.close()  

    " Arquitetura 1"
class LeafSpine(Topo):
    "Cria uma Arquitetura LeafSpine "
    def build(self, n=2):
        """A topologia inicial criada tem 4 Super-Spine e 48 Spine fazendo cada POD que pode ser expandido ate Mega hosts"""
        superspine = 4
        spine = 48
        leafs = {} 
        link_ecmp = 96
        link_delay = '.001ms'
        #spine tambem sao conhecidos como swiches Top of the Rack (TOR)
        switch_type = 'ovsk'

        switches = {}
        hosts = {}
        print '*** Adiciona os Super-Spines                            ***\n'
        for x in range(0, superspine):
            switches[x] = self.addSwitch('cr' + str(x), switch = switch_type)
        for x in range(0, spine):
            switches[x+superspine] = self.addSwitch('er' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+superspine], bw =link_ecmp, delay=link_delay)
        for x in range(0, leafs):
            switches[x+spine] = self.addSwitch('lf' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+spine], bw =link_ecmp, delay=link_delay)
        """
        *** Adiciona os links e controi a topologia                ***
        """
        for x in range(0, superspine):
            #conecta os switches
            for i in range(0, spine):
                self.addLink(switches[x], switches[i+superspine], bw =link_ecmp, delay=link_delay)
                
             for i in range(0, leafs):
                self.addLink(switches[x], switches[i+spine], bw =link_ecmp, delay=link_delay) 

    " Arquitetura 2"
class Fattree(Topo):
    "Cria a arquitetura Fat Tree de acordo com a quantidade especificada"
    def build(self, n=2):
        supersp = 4
        switch_type = 'ovsbk'
        link_ecmp = 10
        link_delay = '.001ms'
        ftsuperspine = {}
        ftspine = {}
        ftleaf = {}
        servers = {}

        for x in range(0, 2):
            ftsuperspine[x] = self.addSwitch('cr'+str(x), switch = switch_type, stp=1)

        for x in range(0,(supersp * 2)):
            ftspine[x] = self.addSwitch('ar'+str(x), switch = switch_type, stp=1 )

        for x in range(0, (supersp *2)):
            ftleaf[x] = self.addSwitch('er'+str(x), switch = switch_type, stp=1 )

        for x in range(0, (supersp *2)):
            servers[x] = self.addHost('h'+str(x))
        for x in range(0,supersp*2, 2):
            self.addLink(ftsuperspine[0], ftspine[x], bw=link_ecmp, delay=link_delay)
            self.addLink(ftsuperspine[1], ftspine[x], bw=10, delay=link_delay)
        for x in range(1, supersp*2, 2):
            self.addLink(ftsuperspine[2], ftspine[x], bw=link_ecmp, delay=link_delay)
            self.addLink(ftsuperspine[3], ftspine[x], bw=10, delay=link_delay)

        for x in range(0, (supersp*2), 2):
            self.addLink(ftspine[x], ftleaf[x], bw=link_ecmp, delay=link_delay)
            self.addLink(ftspine[x], ftleaf[x+1], bw=10, delay=link_delay)
        for x in range(1, (supersp*2), 2):
            self.addLink(ftspine[x], ftleaf[x], bw=link_ecmp, delay=link_delay)
            self.addLink(ftspine[x], ftleaf[x-1], bw=10, delay=link_delay)
        for x in range(0, core*2):
            self.addLink(servers[x], ftleaf[x],
               bw=10, delay=link_delay)                
                

      " Arquitetura 3"
class hybridfattree(Topo):
    "Cria a arquitetura Hybrid Fat-Tree de acordo com a quantidade especificada"
    def build(self, n=2):
        start = 0
        num_cells = 5
        hftsuperspine = 4
        ocs = 1
        switch_type = 'ovsk'
        link_ecmp = 10
        link_delay = '.001ms'
        switches = {}
        servers = {}
        print '*** Adicionando OCS um de cada vez                              ***\n'
        for x in range(0, num_cells):
            switches[x] = self.addSwitch('er' + str(x), switch = switch_type)
            servers[x] = self.addHost('h'+str(x))
            self.addLink(switches[x], servers[x], bw=link_ecmp, delay=link_delay)
            for i in range(0, hftsuperspine):
                name = 'sw' + str(x) +'_' + str(i)
                switches[name] = self.addSwitch(name, switch=switch_type)
                self.addLink(switches[x], switches[name], bw=link_ecmp, delay=link_delay)

        floor = 0
        for x in range(0, num_cells):
            #the D Cell that we want to assign from
            for i in range(floor, hftsuperspine):
                name1 = 'sw' + str(x) +'_' + str(i)
                name2 = 'sw' + str(i+1) +'_' + str(x)
                self.addLink(switches[name1], switches[name2], bw =link_ecmp, delay=link_delay)
            floor = floor +1

 " Arquitetura 4"
class Facebook4post(Topo):
    "Cria uma arquitetura DCN Facebook 4-post"
    def build(self, n=2):
        """A topologia inicial criada tem 4 Super-Spine e 4 Spine fazendo cada POD que pode ser expandido ate Mega hosts"""
        superspine = 4
        spine = 4
        leafs = {}
        link_ecmp = {}
        link_delay = '.001ms'
        #spine tambem sao conhecidos como swiches Top of the Rack (TOR)
        switch_type = 'ovsk'

        switches = {}
        hosts = {}
        print '*** Adiciona os Super-Spines Spine e leafs                           ***\n'
        for x in range(0, superspine):
            switches[x] = self.addSwitch('cr' + str(x), switch = switch_type)
        for x in range(0, spine):
            switches[x+superspine] = self.addSwitch('er' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+superspine], bw =link_ecmp, delay=link_delay)
            
        for x in range(0, leafs):
            switches[x+superspine] = self.addSwitch('lf' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+spine], bw =link_ecmp, delay=link_delay)
        """
        *** Adiciona os links e constroi a topologia                ***
        """
        for x in range(0, superspine):
            #conecta os switches
            for i in range(0, spine):
                
                self.addLink(switches[x], switches[i+superspine], bw =link_ecmp, delay=link_delay)
            
             for i in range(0, leafs):
            
                self.addLink(switches[x], switches[i+leafs], bw =link_ecmp, delay=link_delay)


" Arquitetura 5"
class FacebookNewFabric(Topo):
    "Cria uma arquitetura DCN Facebook New Fabric"
    def build(self, n=2):
        """A topologia inicial criada tem 4 Super-Spine e 48 Spine fazendo cada POD que pode ser expandido ate Mega hosts"""
        superspine = 48
        spine = 4
        leafs =48
        link_ecmp = 192
        link_delay = '.001ms'
        #spine tambem sao conhecidos como swiches Top of the Rack (TOR)
        switch_type = 'ovsk'

        switches = {}
        hosts = {}
        print '*** Adiciona os Super-Spines                            ***\n'
        for x in range(0, superspine):
            switches[x] = self.addSwitch('cr' + str(x), switch = switch_type)
        for x in range(0, spine):
            switches[x+superspine] = self.addSwitch('er' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+superspine], bw =link_ecmp, delay=link_delay)
            
        for x in range(0, leafs):
            switches[x+superspine] = self.addSwitch('lf' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+spine], bw =link_ecmp, delay=link_delay)
        """
        *** Adiciona os links e constroi a topologia                ***
        """
        for x in range(0, superspine):
            #conecta os Switches
            for i in range(0, spine):
                

                self.addLink(switches[x], switches[i+superspine], bw =link_ecmp, delay=link_delay)
                                                   
            for i in range(0, leafs):
            
                self.addLink(switches[x], switches[i+leafs], bw =link_ecmp, delay=link_delay)
                
                
      " Arquitetura 6 caindo um dos links e testando a performance"                
class leafSpinenolink(Topo):
    "Cria a Arquitetura Leaf-Spine com um dos links caindo"
    def build(self, n=2):
       
        superspine = 4
        spine = 48
        Leafs = {}
        link_ecmp = 10
        link_delay = '.001ms'
        no_link_delay = '.001ms'
        switch_type = 'ovsk'

        switches = {}
        hosts = {}
        print '*** Adiciona os switches                           ***\n'
        for x in range(0, 1):
            switches[x] = self.addSwitch('cr' + str(x), switch = switch_type)
        for x in range(0, spine):
            switches[x+superspine] = self.addSwitch('er' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+superspine], bw =link_ecmp, delay=link_delay)
            
         for x in range(0, leafs):
            switches[x+spine] = self.addSwitch('er' + str(x), switch = switch_type)
            hosts[x] =self.addHost('h'+str(x))
            self.addLink(hosts[x], switches[x+spine], bw =link_ecmp, delay=link_delay)    
 
        for x in range(0, 1):
            for i in range(0, spine):

                self.addLink(switches[x], switches[i+superspine], bw =link_ecmp*4, delay=no_link_delay)
            
            for i in range(0, leafs):

                self.addLink(switches[x], switches[i+spine], bw =link_ecmp*4, delay=no_link_delay)    

 " Arquitetura 7 caindo um dos links e testando a performance"
class FatTreeNoLink(Topo):
    def build(self, n=2):
        FTNSuperspine = 4
        switch_type = 'ovsbk'
        link_ecmp = 10
        link_delay = '.001ms'
        FTSuperspine = {}
        FTSpine = {}
        FTLeafs = {}
        servers = {}

        for x in range(0, 2): # supre Spine swiches
            FTSuperspine[x] = self.addSwitch('cr'+str(x), switch = switch_type, stp=1)

        for x in range(0,(FTNSuperspine * 2)): # Aggregate Switches
            FTSpine[x] = self.addSwitch('ar'+str(x), switch = switch_type, stp=1 )

        for x in range(0, (FTNSuperspine *2)): # Edges Switches
            FTLeafs[x] = self.addSwitch('er'+str(x), switch = switch_type, stp=1 )

        for x in range(0, (FTNSuperspine *2)):
            servers[x] = self.addHost('h'+str(x))

        #conecta super spine a Spine
        for x in range(0,FTNSuperspine*2, 2):
            self.addLink(FTSuperspine[0], FTSpine[x], bw=link_ecmp, delay=link_delay)

        for x in range(1, FTNSuperspine*2, 2):
            self.addLink(FTSuperspine[1], FTSpine[x], bw=link_ecmp, delay=link_delay)

        #conecta Spine a Leafs
        for x in range(0, (FTNSuperspine*2), 2):
            self.addLink(FTSpine[x], FTLeafs[x], bw=link_ecmp, delay=link_delay)

        for x in range(1, (FTNSuperspine*2), 2):
            self.addLink(FTSpine[x], FTLeafs[x], bw=link_ecmp, delay=link_delay)

        #conecta os servers aos Leafs
        for x in range(0, FTNSuperspine*2):
            self.addLink(servers[x], FTLeafs[x],
               bw=10, delay=link_delay)
        # cria os links com um caindo
        self.addLink(FTSuperspine[0], FTSuperspine[1], bw =link_ecmp*4)


 " Arquitetura 8 caindo um dos links e testando a performance"
class HybridFatTreeNoLink(Topo):
    def build(self, n=2):
        start = 0
        OCS = 5
        HFTSuperSpine = 1
        HFTLeafs = 1
        switch_type = 'ovsk'
        link_ecmp = 10
        link_delay = '.001ms'
        no_link_delay = '.0005ms'
      

        switches = {}
        hosts = {}
        cr = 'cr0'
        switches[cr] = self.addSwitch(cr, switch=switch_type)
        print '*** Adiciona os switches                              ***\n'
        j=0
        for x in range(0, OCS):
            switches[x] = self.addSwitch('er' + str(x), switch = switch_type)
            for y in range(0, OCS):
                hosts[j] = self.addHost('h'+str(j))
                self.addLink(switches[x], hosts[j], bw=link_ecmp, delay=link_delay)
                j = j +1
            for i in range(0, HFTSuperSpine):
                name = 'sw' + str(x) +'_' + str(i)
                switches[name] = self.addSwitch(name, switch=switch_type)
                self.addLink(switches[x], switches[name], bw=link_ecmp*4, delay=link_delay)
                self.addLink(switches[name], switches[cr], bw=link_ecmp*4, delay=no_link_delay)


        floor = 0
        for x in range(0, OCS):
            #topologia caindo um dos links 
            for i in range(floor, HFTSuperSpine):
                name1 = 'sw' + str(x) +'_' + str(i)
                name2 = 'sw' + str(i+1) +'_' + str(x)
                self.addLink(switches[name1], switches[cr], bw =link_ecmp, delay=no_link_delay)
                self.addLink(switches[name2], switches[cr], bw =link_ecmp, delay=no_link_delay)
            floor = floor +1
        



def perfTest():
     "Cria a rede e executa o teste de performace "
    """Lembrando que os testes disponiveis deve ser trocado o parametro abaixo para cada tipo de toplogia a ser testada"""
    topo = LeafSpine(n=4)
    test = 'LeafSpine'
    run_test = 2 #Parametro 1 testa com Iperf largura de banda e 2 testa o ping
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink, ipBase='172.16.0.0/16')
    packetsize = 1472
    net.start()
    seconds = 100
    net.waitConnected()


    print "Espara a arquitetura convergir"
    net.pingAll()
    host = {}
    
    
    
  print "Comeca os testes"
    if (test == 'Fattree' or test == 'FatTreeNoLink' or test == 'FatTreeTopotest'):
        max_host = 100000
        for y in range(0, max_host):
            host_name = 'h' +str(y)
            host[y] = net.get(host_name)

    elif (test == 'LeafSpine' or test =='LeafSpinenolink' or test == 'Facebook4post' or test == 'FacebookNewFabric' ):
        print "*** Testes arquiteturas baseadas em Leaf Spine ***"
        max_host = 100000
        for y in range(0, max_host):
            host_name = 'h' +str(y)
            host[y] = net.get(host_name)

    elif (test =='HybridFattree' or test == 'HybridFattreenolink'):
        print "***Testes com Hybrid Fattree"
        max_host = 100000
        for x in range(0, max_host):
            host_name = 'h' +str(x)
            print "Adding %s" % host_name
            host[x] = net.get(host_name)    
    
    


    if (run_test == 1):
        print "Testes com IPERF"
        sleep(5)


    elif (run_test ==2 and test =='LeafSpine'):

        print "Teste com ping"
        outfiles, errfiles = {}, {}
        bottom = 0
        for h in range(0, max_host):
            # Create and/or erase output files
            outfiles[ host[h] ] = '/tmp/%s.out' % host[h].name
            errfiles[ host[h] ] = '/tmp/%s.err' % host[h].name
            host[h].cmd( 'echo >', outfiles[ host[h] ] )
            host[h].cmd( 'echo >', errfiles[ host[h] ] )
            # Start pings

            if (h<max_host-1):
                host[h].cmdPrint('ping', host[h+1].IP(), '-s', packetsize,
                        '>', outfiles[ host[h] ],
                        '2>', errfiles[ host[h] ],
                        '&' )
            else:
                host[h].cmdPrint('ping', host[0].IP(), '-s', packetsize,
                        '>', outfiles[ host[h] ],
                        '2>', errfiles[ host[h] ],
                        '&' )


        print "Monitora o arquivo de saida por", seconds, "segundos ou microsegundos"
        f = open('output%s.txt' % str(packetsize), 'w')
        for host[h], line in monitorFiles( outfiles, seconds, timeoutms=500 ):
            if host[h]:
                f.write(line)

        sleep(11)
    elif (run_test ==2 and test !='Fattree'):
        print "Ping Testing"
        outfiles, errfiles = {}, {}
        for h in range(0, max_host):
            # Create and/or erase output files
            outfiles[ host[h] ] = '/tmp/%s.out' % host[h].name
            errfiles[ host[h] ] = '/tmp/%s.err' % host[h].name
            host[h].cmd( 'echo >', outfiles[ host[h] ] )
            host[h].cmd( 'echo >', errfiles[ host[h] ] )
            # Start pings

            if (h<max_host-1):
                host[h].cmdPrint('ping', host[h+1].IP(), '-s', packetsize,
                        '>', outfiles[ host[h] ],
                        '2>', errfiles[ host[h] ],
                        '&' )
            else:
                host[h].cmdPrint('ping', host[0].IP(), '-s', packetsize,
                        '>', outfiles[ host[h] ],
                        '2>', errfiles[ host[h] ],
                        '&' )


        print "Moninotora a saida dos arquivos por", seconds, "segundos ou microsegundos"
        f = open('output%s.txt' % str(packetsize), 'w')
        for host[h], line in monitorFiles( outfiles, seconds, timeoutms=500 ):
            if host[h]:
                f.write(line)



        sleep(11)
    print "Final dos testes"
    net.stop()
    #CLI( net )


if __name__ == '__main__':
    setLogLevel('info')
    perfTest()
