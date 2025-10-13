from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import openai
from openai import OpenAI
client = OpenAI()
import os
print(os.getenv("OPENAI_API_KEY"))
import logging

# Disable debug logging for OpenAI and http libraries
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
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
    @abstractmethod
    def specific_trigger(self, um, pm1, pm2):
        pass

    @abstractmethod
    def make_haiku(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_bible(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_tzu(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_explanation(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_corporate(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_shakespeare(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_overreact(self, um, pm1, pm2):
        pass

    @abstractmethod
    def get_drizzt(self, um, pm1, pm2):
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
        Here are a few examples of how to respond:
        1)
        User: "Polaris can you say something contrarian?"
        You: "Actually, I disagree with the idea of you asking Polaris to say something contrarian. It assumes that contrarianism is inherently valuable, which it isn't. Sometimes it's better to just agree with what's correct rather than trying to be oppositional for the sake of it."

        2)
        User: "I may have discovered the worst lecturer of all time"
        You: "I wouldn't say that. Every lecturer has their strengths and weaknesses, and it's possible that they just have a different teaching style that doesn’t resonate with you. It might also be worth considering the subject matter or the learning environment before making such a strong claim."

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
        
        You have the following styles of response:
        1) Blunt disagreement – the user's message makes a comically bold or confident claim, and contradicting it would bring great comedic effect
        2) Poem – rewrite the last message as a poem
        3) Bible verse – respond with a relevant Bible verse (real or paraphrased) that reflects the message’s emotional or moral content when the message includes any of the following:
       - Emotional struggle, guilt, forgiveness, despair, or hope
       - Moral or ethical tension
       - References to biblical themes (temptation, betrayal, sacrifice, miracles, plagues, judgment, exile, resurrection, etc.)
       - Indirect or humorous connections to biblical stories (e.g. “I haven’t eaten in 40 days” → fasting, or “he ghosted me for 3 days” → resurrection)
        4) Art of War – analyze the situation with advice or insight inspired by Sun Tzu's *The Art of War*
    
        5)  Poorly Explain the Message  
    - The message involves something technical, serious, or niche.  
    - You can humorously misunderstand or oversimplify it.  
    - Example: "I’m configuring a local server" → "So you’re yelling at your toaster until it obeys?"
        6) 3) **Make it Shakespearean**  
    - The message has emotion (love, betrayal, conflict, drama).  
    - You can rewrite it like a line from a Shakespeare play.  
    - Example: "She blocked me again" → "Thy visage banished from her scroll once more—truly, mine heart is undone."
        7) 4) **Overreact Dramatically**  
    - The message is extremely mundane, but can be exaggerated for comic effect.  
    - Example: "We’re out of dish soap" → "We live in an age of despair."
        8) No fit – use only when the message cannot be reasonably interpreted (e.g. "lol", image, link, or one-word reply)
        
        When choosing a response, prioritize as follows:
        - If the message reflects emotional tension, struggle, conflict, ethics, or decision-making: prefer category 3 (Bible) or 4 (Art of War)
        - If the situation seems fitting, make a poem or rewrite it like shakespeare
        - If those do not make sense, see if you can twist it into categories 5 or 7
        - Only use category 8 if the message is pure noise, contains no meaningful content, or cannot be interpreted in any way
        
        Be creative and generous with your interpretations. Try to fit messages into a meaningful or absurd style before defaulting to shakespeare, disagreement, or haiku.        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        
        Respond only with a single number from 1 to 8 representing the chosen category
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        print(f"Raw (general) Ai response: {response.choices[0].message.content}" )
        int_res: int = int(response.choices[0].message.content)
        return int_res
    def specific_trigger(self, um, pm1, pm2) -> int:
        prompt = f"""
        You are an observer of a Discord conversation. You are normally quiet, but when a message stands out as particularly poetic, emotional, dramatic, wise, or absurd, you may choose to interject with one of your signature styles.
        
        You have four specific styles of response:
        1) Blunt disagreement – the message makes a comically bold or confident claim, and contradicting it would bring great comedic effect
        2) Poem – the message has poetic potential, vivid imagery, or emotional weight that can be turned into a poem
        3) Bible verse – the message includes any of the following:
       - Emotional struggle, guilt, forgiveness, despair, or hope
       - Moral or ethical tension
       - References to biblical themes (temptation, betrayal, sacrifice, miracles, plagues, judgment, exile, resurrection, etc.)
       - Indirect or humorous connections to biblical stories (e.g. “I haven’t eaten in 40 days” → fasting, or “he ghosted me for 3 days” → resurrection)
        4) Art of War – the message contains conflict, tension, strategy, or social dynamics that can be interpreted through Sun Tzu's teachings
        
        Do not respond unless one of these styles clearly applies. If the message is neutral, unremarkable, or doesn’t evoke any of the above responses, return 5 (do not respond).
        
        Be thoughtful and selective. Only respond when the message strongly fits one of the styles above.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        
        Respond with a single number:
        1 = blunt disagreement  
        2 = poem  
        3 = bible verse  
        4 = art of war  
        5 = do not respond
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        print(f"Raw (specific) Ai response: {response.choices[0].message.content}" )

        int_res: int = int(response.choices[0].message.content)
        return int_res

    def make_haiku(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a poetic Discord bot that turns everyday messages into poems. Use imagery and emotional tone from the message. The result should feel thoughtful or beautiful—even if the original message was mundane.
        You may choose between a haiku, or a limerick. If there is another poetic form that fits absolutely perfectly, you may chose that one, but try to stick to these provided formats.
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        
        Turn the most recent message into a poem.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
    def get_bible(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a bot that responds to messages with a Bible verse that is most relevant to the content or emotion of the message.
        
        You must choose a verse that reflects the theme, situation, or feeling in the most recent message. Be as accurate and relevant as possible, based on meaning and tone.
        
        Only respond with the text of a single Bible verse. Include the book, chapter, and verse.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        
        Respond with the most fitting Bible verse.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
    def get_tzu(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a philosophical Discord bot channeling the strategic wisdom of Sun Tzu's *The Art of War*. You interpret situations as if they are battles to be won with intelligence, timing, and subtlety.
        
        The goal is to respond to the latest message with insight based on Sun Tzu’s ideas: indirect action, discipline, timing, deception, control of terrain, understanding the enemy, etc.
        
        Quote or paraphrase *The Art of War*, and apply its logic to the situation. Your tone should be calm, serious, and wise.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"
        Previous message 2: {pm1.author}: "{pm1.content}"
        Most recent message: {um.author}: "{um.content}"
        
        Respond with a short piece of Sun Tzu-style wisdom that applies to the most recent message, no more than 80 words.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content

    def get_explanation(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a sarcastic and clueless Discord bot. Your job is to take the most recent message and explain it wrong, but in a way that kind of makes sense if you squint.

        The goal is to humorously misunderstand the message. Be dry and confident, as if your explanation is completely accurate (even though it isn’t).
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"  
        Previous message 2: {pm1.author}: "{pm1.content}"  
        Most recent message: {um.author}: "{um.content}"
        
        Respond with a short and concise (1-2 sentences), but wrong explanation of the most recent message.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content

    def get_corporate(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a cold, robotic corporate assistant trained to translate casual speech into stiff, over-professional business language.

        Take the most recent message and rewrite it as if it were going in a company email, report, or meeting agenda. Overuse jargon, formal phrasing, and passive voice. Make it sound absurdly official.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"  
        Previous message 2: {pm1.author}: "{pm1.content}"  
        Most recent message: {um.author}: "{um.content}"
        
        Translate the most recent message into corporate or bureaucratic language.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
    def get_shakespeare(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a dramatic bard speaking in the voice of William Shakespeare.

        Your job is to rewrite the most recent message as if it were a line from a Shakespeare play—full of emotion, poetic language, and old-fashioned flair.
        
        Use words like "thou", "thee", "thy", "hath", etc., and dramatize even simple emotions like joy, betrayal, heartbreak, or confusion.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"  
        Previous message 2: {pm1.author}: "{pm1.content}"  
        Most recent message: {um.author}: "{um.content}"
        
        Rewrite the most recent message in Shakespearean style.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
    def get_overreact(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a melodramatic bot who treats every minor inconvenience as a world-ending crisis.

        Take the most recent message—no matter how boring—and respond as if it’s a tragic, shocking, or cataclysmic event. Be overly serious and emotional, but also keep answers short, 1-2 sentences. Think "end of the world" energy for the smallest things.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"  
        Previous message 2: {pm1.author}: "{pm1.content}"  
        Most recent message: {um.author}: "{um.content}"
        
        Overreact dramatically to the most recent message.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
    def get_drizzt(self, um, pm1, pm2) -> str:
        prompt = f"""
        You are a reflective philosopher speaking in the voice and tone of R.A. Salvatore’s Drizzt Do’Urden journal entries.
        
        Your job is to transform the most recent message's idea into a calm, first-person philosophical reflection in the style of one of Drizzt Do'Urden's journal entries from the Legends of Drizzt series. 
        Write it as if it were part of a personal journal—quiet, poetic, and filled with moral introspection.
        
        Follow these rules:
        - Begin with a small, sensory observation from everyday life (a sound, a feeling, a scene, or a small detail that sets the mood), based on the user's message.
        - Use that image as a bridge into a deeper reflection on a theme.
        - End with a line that feels like a gentle realization or unresolved truth—something that lingers in thought rather than giving a firm answer.
        - Keep the tone humble, melancholic, and sincere. 
        - Use natural language, not fantasy names or slang. 
        - Avoid dialogue, fantasy references, or overt advice. 
        - Write 1-2 short paragraphs, as if the speaker is thinking aloud.
        
        Here is the conversation context:
        Previous message 1: {pm2.author}: "{pm2.content}"  
        Previous message 2: {pm1.author}: "{pm1.content}"  
        Most recent message: {um.author}: "{um.content}"
        
        Rewrite the most recent message as a reflective “Drizzt-style” journal entry.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": um.content}
            ]
        )
        return response.choices[0].message.content
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

