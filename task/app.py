import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    client = DialClient(
        deployment_name='gpt-4o',
    )
    custom_client = DialClient(
        deployment_name='gpt-4o',
    )
    conversation = Conversation()
    print("Enter system prompt (or press Enter to use default): ")
    system_prompt = input("> ").strip()
    
    if system_prompt:
        conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))
        print("System prompt successfully added to conversation.")
    else:
        conversation.add_message(Message(role=Role.SYSTEM, content=DEFAULT_SYSTEM_PROMPT))
        print(f"No System prompt provided. So, default system prompt added to conversation: {DEFAULT_SYSTEM_PROMPT}")
    print()

    print("Type your question or 'exit' to end the conversation.")
    while True:
        user_input = input("> ").strip()

        if user_input.lower() == 'exit':
            print("Exiting the conversation. Bye!")
            break
        
        conversation.add_message(Message(role=Role.USER, content=user_input))

        print("AI:")
        if stream:
            assistant_message = await client.stream_completion(conversation.get_messages())
        else:
            assistant_message = custom_client.get_completion(conversation.get_messages())
        
        conversation.add_message(assistant_message)



asyncio.run(
    start(True)
)
