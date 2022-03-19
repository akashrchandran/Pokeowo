import datetime
import json
import multiprocessing
import os
import random
import re
import time

import discum


version = 'v0.01'
config_path = 'data/config.json'


logo = f'''
######     ###    ###  ##  #######    ###    ##   ##    ###    
 ##  ##   ## ##    ##  ##   ##  ##   ## ##   ##   ##   ## ##   
 ##  ##  ##   ##   ## ##    ##      ##   ##  ##   ##  ##   ##  
 #####   ##   ##   ####     ####    ##   ##  ## # ##  ##   ##  
 ##      ##   ##   ## ##    ##      ##   ##  #######  ##   ##  
 ##       ## ##    ##  ##   ##  ##   ## ##   ### ###   ## ##   
####       ###    ###  ##  #######    ###    ##   ##    ###    

                                        ~ Pokétwo Autocatcher {version}                         
'''

num_pokemon = 0
shiny = 0
legendary = 0
mythical = 0

poketwo_id = '716390085896962058'

def auto_config():
    global user_token, channel_id
    if not os.path.exists(config_path):
        with open(config_path, "a") as file:
            auth_token = input("Enter you Discord auth token: ")
            channel_id = input("Enter the preferred Channel ID for spamming and catching: ")
            file.write("{\n")
            file.write(f'   "user_token" : "{auth_token}",\n')
            file.write(f'   "channel_id" : "{channel_id}"\n')
            file.write("}")
    os.system('cls' if os.name=='nt' else 'clear')
    with open(config_path,'r') as file:
        info = json.loads(file.read())
        user_token = info['user_token']
        channel_id = info['channel_id']

with open('data/pokemon.txt', 'r', encoding='utf8') as file:
    pokemon_list = file.read()
with open('data/legendary.txt','r') as file:
    legendary_list = file.read()
with open('data/mythical.txt','r') as file:
    mythical_list = file.read()
auto_config()
print(logo)
bot = discum.Client(token=user_token, log=False)

def solve(message):
    hint = [message[i] for i in range(15, len(message) - 1) if message[i] != '\\']
    hint_string = ''.join(hint)
    return re.findall(
        '^' + hint_string.replace('_', '.') + '$', pokemon_list, re.MULTILINE
    )

def spam():
  while True:
    random_number = random.getrandbits(128)
    bot.sendMessage(channel_id, random_number)
    intervals = [2.0,2.1,2.2,2.3,2.4,2.5]
    time.sleep(random.choice(intervals))

def start_spam():
    new_process = multiprocessing.Process(target=spam)
    new_process.start()
    return new_process

def stop(process):
    process.terminate()

def log(string):
    now = datetime.datetime.now()
    current_time = now.strftime('%H:%M:%S')
    print(f'[{current_time}]', string)

@bot.gateway.command
def on_ready(resp):
    if resp.event.ready_supplemental:
        user = bot.gateway.session.user
        log(f'Logged into account: {user["username"]}#{user["discriminator"]}')

@bot.gateway.command
def on_message(resp):
    global spam_process
    if resp.event.message:
        m = resp.parsed.auto()
        if m['channel_id'] == channel_id and m['author']['id'] == poketwo_id:
            if m['embeds']:
                embed_title = m['embeds'][0]['title']
                if 'wild pokémon has appeared!' in embed_title:
                    stop(spam_process)
                    time.sleep(2)
                    bot.sendMessage(channel_id, '<@716390085896962058> h')
                elif "Congratulations" in embed_title:
                    embed_content = m['embeds'][0]['description']
                    if 'now level' in embed_content:
                        stop(spam_process)
                        split = embed_content.split(' ')
                        a = embed_content.count(' ')
                        level = int(split[a].replace('!', ''))
                        if level == 100:
                            #wait will implement in next update
                            pass
                        spam_process = start_spam()
            else:
                content = m['content']
                if 'The pokémon is ' in content:
                    if len(solve(content)) == 0:
                        log('Pokemon not found.')
                    else:
                        for i in solve(content):
                            stop(spam_process)
                            time.sleep(2)
                            bot.sendMessage(channel_id, f'<@716390085896962058> c {i}')
                    time.sleep(2)
                    spam_process = start_spam()

                elif 'Congratulations' in content:
                    global shiny
                    global legendary
                    global num_pokemon
                    global mythical
                    num_pokemon += 1
                    split = content.split(' ')
                    pokemon = split[7].replace('!','')
                    if 'These colors seem unusual...' in content:
                        shiny += 1
                        log(f'A shiny Pokémon was caught! Pokémon: {pokemon}')
                        log(f'Shiny: {shiny} | Legendary: {legendary} | Mythical: {mythical}')
                    elif re.findall(
                        f'^{pokemon}$', legendary_list, re.MULTILINE
                    ):
                        legendary += 1
                        log(f'A legendary Pokémon was caught! Pokémon: {pokemon}')
                        log(f'Shiny: {shiny} | Legendary: {legendary} | Mythical: {mythical}')
                    elif re.findall(f'^{pokemon}$', mythical_list, re.MULTILINE):
                        mythical += 1
                        log(f'A mythical Pokémon was caught! Pokémon: {pokemon}')
                        log(f'Shiny: {shiny} | Legendary: {legendary} | Mythical: {mythical}')
                    else:
                        print(f'Total Pokémon Caught: {num_pokemon}')

                elif 'human' in content:
                    stop(spam_process)
                    log('Captcha Detected; Autocatcher Paused. Press enter to restart.')
                    input()
                    bot.sendMessage(channel_id, '<@716390085896962058> h')

if __name__ == '__main__':
    print('\nEvent Log:')
    spam_process = start_spam()
    bot.gateway.run(auto_reconnect=True)
