import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient:

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        
        }
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }

        response = requests.post(url=self._endpoint, headers=headers, json=request_data)

        if response.status_code == 200:
            response_data = response.json()
            choices = response_data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                print(content)
                return Message(role=Role.ASSISTANT, content=content)
            else:
                raise ValueError("No Choice has been present in the response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._endpoint, headers=headers, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if data != "[DONE]":
                                content_snippet = self._get_content_snippet(data)
                                print(content_snippet, end='')
                                contents.append(content_snippet)
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")
            return Message(role=Role.ASSISTANT, content=''.join(contents))
        #"""
        #Send synchronous request to DIAL API and return AI response.
        #"""

        #TODO:
        # 1. Create headers dictionary with:
        #   - "api-key": self._api_key
        #   - "Content-Type": "application/json"
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        # 4. Check if response.status_code == 200:
        #   - If yes: parse JSON response using response.json()
        #   - Get "choices" from response data
        #   - If choices exist and not empty:
        #     * Extract content from choices[0]["message"]["content"]
        #     * Print the content to console
        #     * Return Message(role=Role.AI, content=content)
        #   - If no choices: raise ValueError("No Choice has been present in the response")
        # 5. If status code != 200:
        #   - Raise Exception with format: f"HTTP {response.status_code}: {response.text}"
        # raise NotImplementedError

        #   async def stream_completion(self, messages: list[Message]) -> Message:
        #"""
        #Send asynchronous streaming request to DIAL API and return AI response.
        #"""
        #TODO:
        # 1. Create headers dictionary with:
        #    - "api-key": self._api_key
        #    - "Content-Type": "application/json"
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Create empty list called 'contents' to store content snippets
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        # 6. Check if response.status == 200:
        #    - If yes: iterate through response.content using 'async for line in response.content:'
        #      * Decode line: line_str = line.decode('utf-8').strip()
        #      * Check if line starts with "data: ":
        #        - Extract data: data = line_str[6:].strip()
        #        - If data != "[DONE]":
        #          + Call self._get_content_snippet(data) to extract content
        #          + Print content snippet without newline: print(content_snippet, end='')
        #          + Append content snippet to contents list
        #        - If data == "[DONE]":
        #          + Print empty line: print()
        #    - If status != 200:
        #      * Get error text: error_text = await response.text()
        #      * Print error: print(f"{response.status} {error_text}")
        # 7. Return Message(role=Role.AI, content=''.join(contents))
        # raise NotImplementedError

    def _get_content_snippet(self, data: str) -> str:
        """
        Extract content from streaming data chunk.
        """
        data = json.loads(data)
        if choices := data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''
