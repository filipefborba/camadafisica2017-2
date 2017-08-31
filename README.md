# Camada Física da Computação - Projeto 1 - Borbafred
- Filipe Borba e Frederico Curti
- Professor : Rafael Corsi
- Auxiliar de ensino : Eng. Eduardo Marossi

# Projeto 1

## Transmissão e recebimento de imagem


O projeto 1 da disciplina de Camada Física da Computação teve por objetivo conectar dois computadores através de um Arduino e transmitir um arquivo de tamanho definido entre os dois. Para tanto, utilizou-se o método de comunicação [LoopBack](https://github.com/Insper/Camada-Fisica-Computacao/wiki/Hardware---Comunica%C3%A7%C3%A3o-modo-LoopBack).


O funcionamento do programa é simples. O arquivo `aplicacao.py` deve ser iniciado através do comando de terminal `python aplicacao.py`; e um papel (Client ou Server) deve ser selecionado.

* Client: seleciona um arquivo e transmite-o para o Server.
* Server: fica sempre pronto para receber um arquivo.

O diagrama a seguir, exemplifica essa relação:  
 
![Imgur](http://i.imgur.com/Bd5pbHv.png)  

Essa dinâmica pode ser resumida em 4 camadas principais de funções: Aplicação (Client e Server), Enlace (Enlace, EnlaceRx, EnlaceTx), Física e Meio. 
* A camada **Aplicação** é aquela que contém o Client e o Server, os quais controlam a programação e são a saída e a entrada do arquivo, respectivamente. 
* A camada **Enlace** é responsável por tornar o canal de comunicação entre o Client e o Server confiável, sendo que o EnlaceRx é para o recebimento e o EnlaceTx é para a transmissão dos arquivos. 
* A camada **Física** é responsável por serializar e desserializar os dados, enquanto que o Meio pode ser visualizado como um fio que conecta a camada Física do Client com a do Server.  

![Imgur](http://i.imgur.com/KGbC4er.png?1)

# Projeto 2

## Criação de um protocolo

Esse projeto consiste na criação de um protocolo de comunicação entre o server e client do [Projeto 1](https://github.com/filipefborba/camadafisica2017-2/wiki/Projeto-1). Isso é realizado através do encapsulamento dos dados a serem enviados e recebidos num pacote que permite uma comunicação mais eficiente entre as partes.
A utilização de um protocolo é benéfica, pois:
* Minimiza erros de envio através de vários pacotes que são checados.
* Permite o envio de arquivos de tamanho desconhecido entre os papéis.

O controle desse pacote é feito através de um cabeçalho (HEAD) e um "fim de pacote" (EOF). Esse controle deve ser igual para os dois papéis, a fim de que haja a comunicação. Esse cabeçalho pode possuir informações importantes, como o tamanho total do arquivo, o tipo de arquivo, um contador para incrementar a cada pacote enviado, entre outras informações relativamente relevantes.

![Imgur](http://i.imgur.com/j4LqFLv.png)

No HEAD, temos:
* Constante Fixa (Int8ub)
* Tamanho do Arquivo (Int16ub)
* Tipo do Arquivo (Array)

Definida a quantiade de bytes reservada para o controle de pacote, podemos calcular o *protocol overhead*, expressa por:
*Overhead = Tamanho Total/Tamanho Payload*
O Overhead desse protocolo é, então, 100,028%.

Throughput é a definião de quão rápido um dado pode ser enviado numa rede, levando em consideração a taxa de envio (baudrate), o overhead de encapsulamento e de serialização. O Baudrate é a taxa em bits por segundo (bps) com a qual uma rede consegue trasmitir bits. A dos arduínos em questão é de 115200 bps.

# Projeto 3

Esse projeto consiste na criação de uma comunicação de confirmação entre o servidor e cliente ("_handshake_"). O Handshake implementado consiste no envio de um pacote "SYN" do cliente, que é respondido pelo servidor por um "SYN+ACK" em caso de sucesso de comunicação ou um "SYN+NACK" em caso de falha. Por fim, se o cliente recebe o SYN+ACK, responde com um ACK e a transferência começa, caso contrário ele tenta enviar um SYN novamente.

O HEAD dos pacotes de comando possui 5 campos: start, size, filename, ext e type (assim como o HEAD do projeto 2!). Os pacotes SYN, ACK, SYN+ACK e SYN+NACK são construídos da mesma forma, porém, seu "type" é diferente. Através do método buildCommandPacket(commandType) é possível construir esses pacotes com types diferentes. No caso, os campos são preenchidos da seguinte maneira no método:
* start = 0xFF
* size = 0x00
* filename = "NULL"
* ext = "NULL"
* type = commandType
sendo commandType uma String contendo "SYN", "ACK, "SYN+ACK" ou "SYN+NACK" (para o caso de um pacote de dados, o tipo é "PAYLOAD").

Os pacotes, então, são representados da seguinte maneira:

![Imgur](http://i.imgur.com/MWvPV7e.jpg)

Depois, as imagens a seguir representam o envio e recepção dos pacotes como uma máquina de estados. Desta forma, é possível visualizar bem o funcionamento do programa:

![Imgur](http://i.imgur.com/yjJItZf.jpg)

![Imgur](http://i.imgur.com/jkEcQQJ.jpg)

Por fim, é possível notar que deve existir um "timeout" para que o programa não fique interrompido na mesma tarefa. O tempo para timeout escolhido foi de 5 segundos, pois consideramos o suficiente para o envio e processamento do handshake.
