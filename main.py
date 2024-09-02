import discord
import random
import asyncio
import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

players = []
impostor = None
word = None
temp_channels = {}
votes = {}
general_channel = None
last_command_time = None
votacao_iniciada = False  



def load_words():
    with open('palavras.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['palavras']



words_list = load_words()



async def votacao():
    global general_channel, impostor, players, votes, word, temp_channels, votacao_iniciada
    if votacao_iniciada:
        return
    votacao_iniciada = True 
    if not players or not impostor:
        await general_channel.send(
            "Nenhuma partida em andamento para iniciar a votação.")
        return

    mentions = ' '.join([player.mention for player in players])
    await general_channel.send(
        f"\n Iniciando a votação! É hora de votar em quem você acha que é o impostor. {mentions} (60) Segundos)\n"
    )
    await general_channel.send("\n Digite `!vote @usuario` para votar. \n")

    def check_vote(msg):
        return msg.channel == general_channel and msg.content.startswith(
            '!vote') and msg.mentions

    votes = {player: 0 for player in players}
    voted = set()

    try:
        while True:
            msg = await client.wait_for('message',
                                        timeout=60,
                                        check=check_vote)
            if msg.mentions:
                voted_player = msg.mentions[0]
                if voted_player in votes:
                    votes[voted_player] += 1
                    await general_channel.send(
                        f'{msg.author.mention} votou em {voted_player.mention}.\n'
                    )

                    # Atualiza e exibe o placar após cada voto
                    placar = '\n'.join(f'{player.mention}: {votes.get(player, 0)} votos'
                                       for player in players)
                    await general_channel.send(f'**Placar Atual:**\n{placar}')
                    
                   
                    if len(voted) == len(players)-1:
                        
                        #print(len(players))
                        break
                    voted.add(msg.author)

    except asyncio.TimeoutError:
        pass

  
    if all(v == 0 for v in votes.values()):
        await general_channel.send(
            "\n Ninguém votou! O impostor escapou sem ser descoberto.\n")
    else:
        most_voted = max(votes, key=votes.get, default=None)
        if most_voted:
            if most_voted == impostor:
                await general_channel.send(
                    f'{most_voted.mention} foi acusado e era o impostor! Vocês venceram! A Palavra era: {word}\n \n'
                )
            else:
                await general_channel.send(
                    f'{most_voted.mention} foi acusado, mas não era o impostor. O impostor era {impostor.mention}. A Palavra era: {word}\n'
                )

    for channel in temp_channels.values():
        await channel.delete()
    temp_channels = {}

    if general_channel:
        await general_channel.send(
            "\n O canal será excluído após 15 minutos de inatividade.\n")

   
    impostor = None
    word = None
    votes.clear()
    votacao_iniciada = False


@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}!')
    client.loop.create_task(check_inactivity())


@client.event
async def on_message(message):
    global players, impostor, word, temp_channels, votes, general_channel, last_command_time, votacao_iniciada

    #print(message.content)
    if message.author == client.user:
        return

    last_command_time = message.created_at

    if message.content.startswith('!join'):
        if message.author.voice:
            if message.author not in players:
                players.append(message.author)
                votes[message.author] = 0
                await message.channel.send(
                    f'{message.author.mention} entrou na partida!')
            else:
                await message.channel.send(
                    f'{message.author.name}, você já está na partida!')
        else:
            await message.channel.send(
                'Você precisa estar em um canal de voz para se juntar ao jogo.'
            )

    if message.content.startswith('!start'):
        if len(players) < 0:
            await message.channel.send(
                "Precisa de pelo menos 3 jogadores para iniciar!")
            return

        guild = message.guild
        votacao_iniciada = False
        for channel in temp_channels.values():
            await channel.delete()
        temp_channels = {}

        impostor = random.choice(players)
        word = random.choice(words_list)

       
        player_order = random.sample(players, len(players))

       
        order_message = "Ordem de quem deve falar:\n"
        order_message += "\n".join(f"{i+1}. {player.mention}"
                                   for i, player in enumerate(player_order))
        await message.channel.send(order_message)

        for player in players:
            temp_channel = await guild.create_text_channel(
                f'jogo-{player.name}',
                overwrites={
                    guild.default_role:
                    discord.PermissionOverwrite(read_messages=False),
                    player:
                    discord.PermissionOverwrite(read_messages=True),
                    client.user:
                    discord.PermissionOverwrite(read_messages=True)
                })
            temp_channels[player] = temp_channel

            if player == impostor:
                await temp_channel.send(
                    f'{player.mention} Você é o impostor! Finja conhecer a palavra.'
                )
            else:
                await temp_channel.send(f'{player.mention} A palavra é: {word}'
                                        )

        general_channel = discord.utils.get(guild.text_channels,
                                            name='quem-e-o-impostor')
        if not general_channel:
            general_channel = await guild.create_text_channel(
                'quem-e-o-impostor',
                overwrites={
                    guild.default_role:
                    discord.PermissionOverwrite(read_messages=True),
                    client.user:
                    discord.PermissionOverwrite(read_messages=True)
                })

        else:
            await general_channel.edit(
                overwrites={
                    guild.default_role:
                    discord.PermissionOverwrite(read_messages=True),
                    client.user:
                    discord.PermissionOverwrite(read_messages=True)
                })

        await general_channel.send(
            "\n O jogo começou! Cada um irá receber uma mensagem em um canal privado.\n"
        )
        print(word)

      
        await asyncio.sleep(180)
        if players or impostor:
            await votacao()  
            if not votacao_iniciada:  
                await votacao()
    if message.content.startswith('!votacao'):
        await votacao() 

    if message.content.startswith('!reset'):
        players = []
        impostor = None
        word = None
        votes = {}

      
        for channel in temp_channels.values():
            if channel and channel != general_channel:
                await channel.delete()
        temp_channels = {}

       
        if general_channel and general_channel in message.guild.text_channels:
         
            await general_channel.send("O jogo foi reiniciado.")

    
        general_channel = None

    if message.content.startswith('!placar'):
        if not players:
            await message.channel.send("Nenhum jogo está em andamento.")
            return

        placar = '\n'.join(f'{player.mention}: {votes.get(player, 0)} votos'
                           for player in players)
        await message.channel.send(f'**Placar Atual:**\n{placar}')

    if message.content.startswith('!regras'):
        regras = (
            "**Regras do Jogo Quem é o Impostor?**\n\n"
            "1. Todos os jogadores devem estar em um canal de voz para participar.\n\n"
            "2. Use `!join` para entrar no jogo.\n\n"
            "3. Quando o jogo começar, cada jogador receberá uma palavra em um canal privado.\n\n"
            "4. O impostor deve fingir conhecer a palavra e enganar os outros jogadores.\n\n"
            "5. Após 3 minutos, começará a votação. Cada jogador deve votar em quem acha que é o impostor usando `!vote @usuario`.\n\n"
            "6. O jogador com mais votos é acusado.\n\n"
            "7. Se o acusado for o impostor, os jogadores venceram. Caso contrário, o impostor vence.\n\n"
        )
        await message.channel.send(regras)

    if message.content.startswith('!players'):
        if not players:
            await message.channel.send("Nenhum jogador está na partida.")
            return

        players_list = ' '.join(f'{player.mention}' for player in players)
        await message.channel.send(f'**Jogadores Ativos:**\n{players_list}')

    if message.content.startswith('!comandos'):
        comandos = (
            "**Lista de Comandos:**\n\n"
            "`!join`\n"
            "Descrição: Permite que o usuário entre na partida.\n"
            "Requisitos: O usuário deve estar em um canal de voz para se juntar ao jogo.\n"
            "Ação: Adiciona o usuário à lista de jogadores e cria uma entrada para ele no placar.\n\n"

            "`!start`\n"
            "Descrição: Inicia o jogo.\n"
            "Requisitos: Pelo menos 3 jogadores devem estar na partida.\n"
            "Ação: Seleciona um impostor aleatório, escolhe uma palavra aleatória e cria canais de texto privados para cada jogador. Após 3 minutos, inicia a votação.\n\n"

            "`!votacao`\n"
            "Descrição: Inicia a votação manualmente.\n"
            "Ação: Começa a votação, onde os jogadores devem votar em quem acham que é o impostor. Se a votação já tiver sido iniciada, o comando não terá efeito.\n\n"

            "`!reset`\n"
            "Descrição: Reinicia o jogo.\n"
            "Ação: Remove todos os jogadores da partida, exclui os canais temporários (exceto o canal geral) e reinicializa o estado do jogo. O canal geral não é excluído, mas é limpo.\n\n"

            "`!placar`\n"
            "Descrição: Mostra o placar atual.\n"
            "Ação: Exibe o número de votos que cada jogador recebeu.\n\n"

            "`!regras`\n"
            "Descrição: Mostra as regras do jogo.\n"
            "Ação: Envia uma mensagem com as regras do jogo.\n\n"

            "`!players`\n"
            "Descrição: Lista os jogadores ativos.\n"
            "Ação: Exibe a lista de jogadores atualmente na partida.\n"
        )
        await message.channel.send(comandos)



async def check_inactivity():
    global general_channel, last_command_time
    await client.wait_until_ready()

    while True:
        await asyncio.sleep(60)
        if general_channel and last_command_time:
            now = discord.utils.utcnow()
            if (now - last_command_time).total_seconds() > 900:
                await general_channel.delete()
                #general_channel = None


client.run('Sua_api')
