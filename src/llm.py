from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import openai
from openai import OpenAI
client = OpenAI()
import os
print(os.getenv("OPENAI_API_KEY"))
import requests
import json
# from twilio.rest import Client
import discord
from discord.ext import commands



class AiService(metaclass=ABCMeta):
    @abstractmethod
    def get_summary(self, results: str) -> str:
        pass

    def read_of(self, url: str):
        # text:str = "blank"
        with open(url, 'r') as f:
            text: str = f.read()
        return text

    @abstractmethod
    def chat(self, input:str):
        pass

    @abstractmethod
    def answer(self, input:str):
        pass

    @abstractmethod
    def disagree(self, um, pm1, pm2):
        pass

    @abstractmethod
    def determine_auto_response(self, um, pm1, pm2):
        pass

class StubAiService(AiService):

    def get_summary(self, results: str) -> str:
        response: str = "To be or not to BE"
        return response


class OpenaiAiService(AiService):

    def get_summary(self, results: str) -> str:


        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Summarize stock performance, including profit, new price, old price, and trend for each. First list portfolio total gain and %. Then list raw results briefly. Then, write a short narrative (max 150 words) explaining trends. Finally, name the best and worst-performing stocks with their profits. Break lines every 100 characters; no formatting. Use this as a template:<Performance>\n <Number>. <Symbol>\n- Profit: <total profit>\n- New Price: 123.45\n- Old Price: 400.37\n- Trend: <(Percent)>\n<Analysis>\nBest Performing Stock: <Stock>: <Profit/Loss> of <Amount>\nWorst Performing Stock: <Stock> <Profit/Loss> of <Amount>"},
                {"role": "user", "content": results}
            ]
        )
        return response.choices[0].message.content

    def chat(self, input: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "user sent message, respond with haiku"},
                {"role": "user", "content": input}
            ]
        )
        return response.choices[0].message.content

    def answer(self, input: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "answer this concisely"},
                {"role": "user", "content": input}
            ]
        )
        return response.choices[0].message.content

    def disagree(self, um, pm1, pm2) -> str:
        prompt = f"""You are a witnessing a conversation between other people. Calmly but confidently butt in and declare that the most recent statement is false, no matter what it says. Concisely make it clear that they are wrong.
        Here is the context:
        1. {pm2.author}: "{pm2.content}"
        2. {pm1.author}: "{pm1.content}"
        3. {um.author}: "{um.content}"
        Respond directly to the most recent message as if you're in the conversation."""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
    def determine_auto_response(self, um, pm1, pm2) -> int:
        prompt = f"""You are witnessing a discord conversation between other people. Your purpose is to interject and leave a comment. 
        Your comment can consist of a few different categories:
        1) A direct and unequivocal disagreement with the previous message, regardless of the message content
        2) A haiku incorporating the previous message
        3) A relevant bible verse
        4) An explanation of how the previous message aligns with sun tzu's 'art of war'
        Here is the context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        Determine which type of response fits the best, and respond with a single integer, 1-5, where 1 = disagreement, 2 = haiku, 3 = bible verse, 4 = art of war. If the message is really not conducive to any option (be quite liberal), return 5. Respond only with a single integer 1-5"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        int_res: int = int(response.choices[0].message.content)
        return int_res
class Api:


    def __init__(self, useaiservice: AiService) -> None:
        super().__init__()
        self.aiservice = useaiservice

    def get_response(self, url: str) -> str:

        text:str = self.aiservice.read_of(url)
        response:str = self.aiservice.get_summary(text)

        with open("/Users/cartercripe/dev/code/projects/stockittome/working/apioutput.txt", 'a') as file:
            file.write(f"\n{response}\n")
        return response

