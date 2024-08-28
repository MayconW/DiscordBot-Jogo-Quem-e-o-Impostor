Quem é o Impostor? - Jogo Interativo no Discord

Este projeto é um bot para Discord que implementa o jogo "Quem é o Impostor?". Inspirado em jogos de dedução social, o bot permite que jogadores se juntem em um canal de voz, recebam palavras secretas, e tentem descobrir quem entre eles está fingindo conhecer a palavra correta.
Funcionalidades

    Comandos Interativos: Use comandos simples como !join, !start, !vote, e !reset para controlar o jogo.
    Seleção Aleatória de Impostor e Palavra: Um impostor é selecionado aleatoriamente, e todos os jogadores, exceto o impostor, recebem uma palavra secreta.
    Votação: Após um período de discussão, os jogadores votam em quem eles acreditam ser o impostor.
    Canais Privados Temporários: Canais de texto privados são criados para cada jogador, onde eles recebem suas instruções secretas.
    Placar e Resultados: O bot acompanha os votos e revela o impostor após a votação, exibindo o placar e o resultado final.
    Inatividade e Limpeza Automática: Se o jogo ou canal geral ficar inativo por mais de 15 minutos, o canal é automaticamente deletado para manter a organização.

Como Usar

    Inicie o Bot: Faça o deploy do bot no seu servidor Discord e execute-o.
    Entre no Jogo: Use o comando !join para participar do jogo.
    Comece o Jogo: Com pelo menos 3 jogadores, use !start para iniciar.
    Votação: Após a discussão, use !vote @usuario para votar no jogador que você acredita ser o impostor.
    Reiniciar: Após o término de uma partida, use !reset para reiniciar o jogo.

Requisitos

    Python 3.7+
    discord.py: Biblioteca do Discord para Python.
    Palavras JSON: Arquivo palavras.json contendo uma lista de palavras.

Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.
