import json
from typing import Optional

import openai


class OpenAIChatHelper:
    """Uses the OpenAI's API and stores previous messages to allow ChatGPT like chats."""

    def __init__(
        self,
        api_key: str,
        primer_prompt: str = "You are an AI assistant",
        model: Optional[str] = "gpt-3.5-turbo",
        temperature: Optional[float] = 0.75,
        max_tokens: Optional[int] = 1000,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # set primer. According to OpenAI it does not always pay attention to system messages,
        # so duplicate as user messages.
        self.messages = [
            {"role": "system", "content": primer_prompt},
            {"role": "user", "content": f"{primer_prompt} Do you understand?"},
            {"role": "assistant", "content": "Yes I understand."},
        ]
        openai.api_key = self.api_key

    def generate_chat_completion(self):
        """Wrapper around the ChatCompletion class of openai.
        Provides less flexibility than using the endpoint itself."""

        return openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def continue_chat(self, user_prompt):
        self.messages.append(
            {"role": "user", "content": user_prompt},
        )

        chat = self.generate_chat_completion()
        # print(chat)
        reply = chat.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def chat(self):
        """Open loop to begin chatting and add previous message to messages to keep context."""

        while True:
            message = input("User: ")
            if message:
                # saves user message to context.
                self.messages.append(
                    {"role": "user", "content": message},
                )

                chat = self.generate_chat_completion()
                reply = chat.choices[0].message.content

            print(f"ChatGPT: {reply}")
            # saves gpt message to context.
            self.messages.append({"role": "assistant", "content": reply})


class OpenAIHelper:
    def __init__(self, api_key_file: str = "openai-secret.json"):
        openai.api_key = get_api_key_from_file(api_key_file)

    def models(self):
        return openai.Model.list()

    def retrieve_model(self, model: str):
        return openai.Model.retrieve(model)

    def generate(self, prompt, model="text-davinci-003", temp=0.75, max_tokens=1000):
        resp = openai.Completion.create(
            model=model, prompt=prompt, temperature=temp, max_tokens=max_tokens
        )
        return resp