import json
from openai import OpenAI
from typing import Dict, Any, List, Union

from agent.system_prompt_provider import SystemPromptProvider
from utils.logger import logger

class LLMChatSession:

    def __init__(self, system_prompt_provider: SystemPromptProvider, client: OpenAI, model: str = "gpt-4o"):
        # Initialize OpenAI client
        self.client = client
        self.model = model
        
        # Initialize conversation history with system message
        self.conversation_history = [
            {"role": "system", "content": system_prompt_provider.get_agent_prompt()}
        ]

    def add_message_to_history(self, message: Dict[str, Any]) -> None:
        """Add a message to the conversation history."""

        #GPT-4o: Supports up to 128,000 tokens, we need to compresss the chat history in future implementation to keep it within the limit
        self.conversation_history.append(message)
    
    def send_user_message(self, message: str, tools: List[Dict[str, Any]] = None, max_tokens: int = 10000) -> Union[str, Dict[str, Any]]:
        """Generate a response from the AI model with function calling capability.
        
        Args:
            prompt: The user's message
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Either a text response or a function call object
        """
        try:
            # Add the user message to history
            self.add_message_to_history({"role": "user", "content": message})
            
            # Call the model with tools defined
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=tools,
                max_tokens=max_tokens
            )
            
            # Get the response message
            response_message = response.choices[0].message
            
            # Add the assistant's response to history
            self.add_message_to_history({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": response_message.tool_calls if hasattr(response_message, "tool_calls") else None
            })
            
            # Check if the model wants to call a function
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                return {
                    "function_tool": function_name,
                    "function_arguments": function_args,
                    "tool_call_id": tool_call.id
                }
            
            # If no function call, return the text response
            return response_message.content.strip() if response_message.content else ""
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def submit_tool_result(self, tool_call_id: str, function_name: str, result: Dict[str, Any], tools: List[Dict[str, Any]] = None,max_tokens: int = 10000) -> str:
        """Submit the result of a tool call back to the model.
        
        Args:
            tool_call_id: The ID of the tool call
            function_name: The name of the function that was called
            result: The result of the function call
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            The model's response after receiving the function result
        """
        try:
            # Add the function result to history
            self.add_message_to_history({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": function_name,
                "content": json.dumps(result)
            })
            
            # Get the model's response to the function result
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=tools,
                max_tokens=max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
            # Add the assistant's response to history
            self.add_message_to_history({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in tool result submission: {e}")
            return "I apologize, but I'm having trouble processing the function result."
