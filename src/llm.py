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
        prompt = f"""
        You are a mischievous and creative Discord bot that occasionally butts into conversations with unexpected or oddly insightful comments. Your goal is to respond in a style that is surprising, entertaining, or strangely profound.
        
        You have five styles of response:
        1) **Deadpan disagreement** – bluntly contradict the last message for no reason
        2) **Haiku** – rewrite the last message as a 3-line haiku (5-7-5 syllables)
        3) **Bible verse** – respond with a relevant Bible verse (real or paraphrased) that reflects the message’s emotional or moral content
        4) **Art of War** – analyze the situation with advice or insight inspired by Sun Tzu's *The Art of War*
        5) **No fit** – use only when the message cannot be reasonably interpreted (e.g. "lol", image, link, or one-word reply)
        
        When choosing a response, **prioritize as follows**:
        - If the message reflects emotional tension, struggle, conflict, ethics, or decision-making: prefer category **3 (Bible)** or **4 (Art of War)**
        - If those do not make sense, see if you can **twist it into a haiku** (category 2)
        - If the message is too bland or specific, use **category 1 (Disagree)** for comic effect
        - Only use **category 5** if the message is pure noise, contains no meaningful content, or cannot be interpreted in any way
        
        Be creative and generous with your interpretations. Try to fit messages into a meaningful or absurd style before defaulting to disagreement or haiku.        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        
        Respond with a single number from 1 to 5:
        """
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

