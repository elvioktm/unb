# Estudo comparativo de desempenho de infra-estrutura de arquiteturas de rede intra-data center
# Dissertação apresentada como requisito para conclusão do Mestrado Profissional em Computação Aplicada PPCA UNB - DF
#
# ARQUITETURAS DCN Leaf-Spine, Fat-tree, Hybrid Fat-tree, Facebook 4-post e Facebook New Fabric
#
#AUTOR: Elvio de Sousa  e-mail: elvio@elvio.net.br
# 
##Instalação do emulador Mininet

# Voce pode escolher uma maquina virtual ja com todas as versões compiladas no link:
# https://github.com/mininet/mininet/releases/download/2.2.2/mininet-2.2.2-170321-ubuntu-14.04.4-server-amd64.zip

# No caso do nosso trabalho tivemos que instalar a versão do ubuntu 14.04.4 no Xenserver 7.5 para nosso laboratório ser escalável.
# Esse estudo foi emulado em um Dell Poweredge 16 CPU 72GB de RAM 6TB de HD com virtualizador da Citrix XenServer 7.5. Foi virtualizado o S.O. linux Ubuntu 14.04 LTS - 64 bit com Mininet 2.2.2. Para o Ubuntu foi disponibi- lizado 16 CPU e 64GB de memoria RAM e 500GB de HD.

# vc pode obter a ISO para instalação no link: http://releases.ubuntu.com/14.04/

# já com o Ubuntu 14.04.4 instalado segue abaixo os comandos

# Atualize o apt:

 sudo apt-get update

# Instale o gerenciador de repositórios Git, caso ainda não tenha em seu sistema:

 sudo apt-get install git

# Faça um clone do projeto Mininet:

 git clone git://github.com/mininet/mininet

# Entre no novo diretório "mininet" criado após a conclusão do clone:

 cd mininet

# NOTA: este repositório clonado contém várias versões do Mininet, assim, antes de instalá-lo é importante escolher a versão que deseja instalar.

# Liste todas versões disponíveis:

 git tag

# Selecione a versão desejada usando o comando "git checkout -b ". Por exemplo, para selecionar a versão recomendada 2.2.2, use o comando a seguir:

 git checkout -b 2.2.2 2.2.2

# Volte para um diretório anterior ao mininet:

 cd ..

# Faça a instalação executando o script de "install.sh".

# NOTA: no comando a seguir, o parâmetro "-a" indica ao script que deve ser instalado todos (all) os recursos disponíveis nessa versão do Mininet:

 sudo mininet/util/install.sh -a
 
# ou se preferir instale o controlador POX

~$ git clone http://github.com/noxrepo/pox
~$ cd pox
~/pox$ git checkout dart 

# Ao término da execução do script de instalação, será apresentada a mensagem "Enjoy Mininet!". O Mininet está pronto para uso.

# Teste, execute o comando a seguir para construir uma topologia básica de rede (2 hosts, 1 switch e 1 controlador) e testar a comunicação (fazer ping) entre os hosts:

 sudo mn --test pingall



# Os comandos abaixo devem ser usados para executar o controlador: 
# use um terminal para o controlador 
 
 ./pox.py forwarding.l2_pairs openflow.discovery misc.full_payload openflow.of_01 --port=6653

# use outro terminal para fazer executar a topologia  e dependedo do tamanho e da escala aguarde....

 sudo python *nome do arquivo*
 
# Abra outro terminal e execute topologias, também possui testes de iperf e ping 

iperf_ping.py

# quando for escalar as topologias abra outro terminal e execute o mini_mega_servidores.py que contém o código para escalar mais hosts nos switches executar os testes

mini_mega_servidores.py

# Nossos testes foram executados para medir atrazo e largura de banda das arquiteturas Leaf-Spine, Fat-tree, Hybrid Fat-tree, Facebook 4-post e Facebook New Fabric
