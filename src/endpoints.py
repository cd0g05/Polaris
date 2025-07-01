import os
import sys
from abc import abstractmethod, ABCMeta
import random

import discord
import requests
from discord import Intents, Client, Message
from src.data_retriever import StockPriceRetriever
from src.llm import AiService
# from src.messager import send_message


# class EndpointBase(metaclass=ABCMeta):
#
#     @abstractmethod
#     async def send_message(self, message: Message, user_message: str) -> None:
#         pass
#
#     @abstractmethod
#     async def on_message(self, message: Message) -> None:
#         pass


class DiscordEndpoint():

    def __init__(self, data_retriever: StockPriceRetriever, llm: AiService):
        super().__init__()
        self.intents: Intents = Intents.default()
        self.intents.message_content = True  # NOQA
        self.client: Client = Client(intents=self.intents)
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.data_retriever: StockPriceRetriever = data_retriever
        self.llm: AiService = llm
        self.client.run(token=os.getenv('TOKEN'))


    def get_response(user_input: str) -> str:
        lowered: str = user_input.lower()

        if lowered == '':
            return 'Well, you\'re awfully silent...'
        elif 'hello' in lowered:
            return 'Hello there!'
        elif 'how are you' in lowered:
            return 'Good, thanks!'
        elif 'bye' in lowered:
            return 'See you!'
        else:
            return 'Not supported'

    def get_rand_num(self, num) -> bool:
        if random.randint(1, num) == 1:
            return True
        return False
    # STEP 2: MESSAGE FUNCTIONALITY
    async def send_message(self, message: Message, response: str, is_private: bool) -> None:

        try:
            await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print(e)


    async def on_ready(self) -> None:
        print(f'{self.client.user} is now running!')


    # STEP 4: HANDLING INCOMING MESSAGES
    async def on_message(self, message: Message) -> None:
        if message.author == self.client.user:
            return

        username: str = str(message.author)
        user_message: str = message.content
        channel: str = str(message.channel)

        print(f'[{channel}] {username}: "{user_message}"')
        if user_message[0] != '$':
            # if self.get_rand_num(8):
            history = [msg async for msg in message.channel.history(limit=3, before=message)]
            if len(history) >= 2:
                previous_message_1 = history[0]
                previous_message_2 = history[1]
                message_choice:int = self.llm.disagree(message, previous_message_1, previous_message_2)
                print(message_choice)
                return
        #         res = self.llm.disagree(message, previous_message_1, previous_message_2)
            #         await self.send_message(message, res, False)
            #     else:
            #         await self.send_message(message, "Some error happened, contact carter", False)
            else:
                return
        # and user_message[0] != 'Wordle'
        else:
        #     if user_message[0] == 'Wordle':
        #         if user_message[2] == 'X/6':
        #             await self.send_message(message, "You'll get em next time!", False)
        #             return
        #         elif user_message[2] == '4/6' or user_message[2] == '5/6' or user_message[2] == '6/6':
        #             await self.send_message(message, "Thats a tough one!", False)
        #             return
        #         else:
        #             await self.send_message(message, "Nice Job!", False)
        #             return

            user_message = user_message[1:]
            if is_private := user_message[0] == '?':
                user_message = user_message[1:]

            toks = user_message.split(' ')
            command: str = toks[0]
            if command == 'stock':
                symbol: str = toks[1]
                price: float = self.data_retriever.get_stock_price(symbol)
                #this is where i would then pass the data to the llm to get a richer response if i wanted to
                await self.send_message(message, f'Price of {symbol}: {price:0.2f}', is_private)
            elif command == 'haiku':
                input:str = " ".join(toks[1:])
                response:str = self.llm.chat(input)
                await self.send_message(message, response, is_private)
            elif command == 'echo':
                input:str = " ".join(toks[1:])
                response:str = input
                await self.send_message(message, response, is_private)
            elif command == 'joke':
                url = 'https://v2.jokeapi.dev/joke/Any?blacklistFlags=racist,sexist,explicit'
                r = requests.get(url)
                joke = r.json()
                output:str = 'ERROR'
                if joke['type'] == 'twopart':
                    setup:str = joke['setup']
                    delivery:str = joke['delivery']
                    output = f'{setup}\n\n{delivery}'
                else:
                    output = joke['joke']
                await self.send_message(message, output, is_private)
            elif command == 'ask':
                inpt:str = " ".join(toks[1:])
                response:str = self.llm.answer(inpt)
                await self.send_message(message, response, is_private)
            elif command == 'request':
                inpt:str = "**Request:**\n------------------------------\n"
                inpt += " ".join(toks[1:])

                inpt += f"\n------------------------------\n*Message from {str(message.author.name)} | id: {str(message.author.id)}*"
                admin_uid:int = 393400676077797386
                admin:discord.User = await self.client.fetch_user(admin_uid)
                await admin.send(inpt)
            elif command == 'msg':
                target_uid:int = int(toks[1])
                target:discord.User = await self.client.fetch_user(target_uid)
                inpt:str = f"**Message from {str(message.author.name)} | **"
                inpt += " ".join(toks[2:])
                try:
                    await target.send(inpt)
                except discord.Forbidden:
                    await self.send_message(message,f"Could not send a DM to {target.name}. They might have DMs disabled or blocked the bot.", False)
            elif command == 'welcome':
                admin_uid:int = 393400676077797386
                if message.author.id == admin_uid:
                    user_id:int = int(toks[1])
                    target:discord.User = await self.client.fetch_user(user_id)
                    response:str = (f"Hello {target.name}, I am **Polaris**, a Discord Bot created by *Carter Cripe*. "
                                    "\n"
                                    "\nWhile I have many functions, My primary purpose is to guide people to the answers to their questions"
                                    "\n"
                                    "\nHere is the current list of supported commands: "
                                    "\n"
                                    "\n**$ask <question>** : The bot will answer your question"
                                    "\n**$answer** : The bot will give it's answer to the previous message in the channel"
                                    "\n**$haiku <question>** : The bot will answer your question in the form of a haiku "
                                    "\n**$joke** : The bot will tell you a funny joke"
                                    "\n**$stock <stock symbol>** : The bot will give the current price of the given stock "
                                    "\n**$request <feature>**: You can request a new feature for this bot"
                                    "\n**$msg <user_id> <message>**: Directly messages the user the message (requires user_id)"
                                    "\n**$help** : The bot will display a help menu"
                                    "\n"
                                    "\nThank you for using Polaris! Enjoy!")
                    try:
                        await target.send(response)
                    except discord.Forbidden:
                        await self.send_message(message,f"Could not send a DM to {target.name}. They might have DMs disabled or blocked the bot.", False)
                else:
                    await self.send_message(message, "*You do not have permission to use that command!*", False)
            elif command == 'help':
                response:str = ("Hello, I am **Polaris**, a Discord Bot created by *Carter Cripe*. "
                                "\n"
                                "\nHere is the current list of supported commands: "
                                "\n"
                                "\n**$ask <question>** : The bot will answer your question"
                                "\n**$answer** : The bot will give it's answer to the previous message in the channel"
                                "\n**$haiku <question>** : The bot will answer your question in the form of a haiku "
                                "\n**$joke** : The bot will tell you a funny joke"
                                "\n**$stock <stock symbol>** : The bot will give the current price of the given stock "
                                "\n**$request <feature>**: You can request a new feature for this bot"
                                "\n**$msg <user_id> <message>**: Directly messages the user the message (requires user_id)"
                                "\n**$help** : The bot will display a help menu"
                                "\n"
                                "\nIf you would like the response via a private message, include a '?' in the command - i.e: $?stock AMD "
                                "\nIf you have any further questions, contact Carter Cripe at *(970) 581-8720*.")
                await self.send_message(message, response, is_private)

            else:
                await self.send_message(message, 'Invalid Command', is_private)

        # await self.send_message(message, user_message)


# class EmailEndpoint(EndpointBase):
#
#     async def send_message(self, message: str):
#         pass