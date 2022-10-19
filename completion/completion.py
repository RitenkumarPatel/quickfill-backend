import re

import openai
from transformers import pipeline


class Completion:
    """Class for interacting with the OpenAi Completion API."""

    def __init__(self, api_key):
        openai.api_key = api_key

    @staticmethod
    def __create_prompt(document: str) -> str:
        summarizer = pipeline("summarization")
        document = document.replace("\n", " ")
        sentences = [
            sentence.strip() for sentence in re.split("[.!?\n]", document)
            if sentence != ""
        ]
        summary = summarizer(document,
                             max_length=130,
                             min_length=30,
                             do_sample=False)[0]["summary_text"]
        if sentences:
            prompt = ("Finish the below sentence:\n\n"
                      "Example: > The mitochondria\n"
                      "Output: are the powerhouse of the cell.\n\n"
                      f"Here is some context:\n{summary}\n\n"
                      f"> {sentences[-1]}")
            return prompt

    @staticmethod
    def __fetch_response(prompt: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0.05,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response["choices"][0]["text"]

    def fetch_autocomplete(self, document: str) -> str:
        """Prompts the OpenAi Completion API.

        Creates an OpenAi Completion API prompt and then sends a request with
        the prompt to the OpenAi Completion API.

        :param document: The document inputted to create the OpenAi Completion
            API prompt.

        :return: A response sent by the OpenAi Completion API.
        """
        prompt = self.__create_prompt(document)
        response = self.__fetch_response(prompt)
        response = response.replace(" . ", ". ").replace(" .", ". ")
        return response
