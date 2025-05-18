from openai import OpenAI
from agent.llm_chat_session import LLMChatSession
from tools.function_tools import FunctionTools
from agent.system_prompt_provider import SystemPromptProvider
from utils.logger import logger

class SupportAgent:
    
    def __init__(self, system_prompt_provider: SystemPromptProvider, function_tools: FunctionTools, openai_client: OpenAI):
        """Initialize the conversation manager.
        
        Args:
            ai_service: The AI service for generating responses
        """
        
        self.function_tools = function_tools
        # constructing a new LLM chat session per support agent instance
        self.llm_chat_session = LLMChatSession(system_prompt_provider=system_prompt_provider, client=openai_client)
        

    def process_message(self, message: str) -> str:
        """
        Process a user message and handle any function tool requests.
        
        This method sends the user's message to the AI and enters a loop to process
        any function calls until a user-facing response is received.
        
        Args:
            message: The user's message
            
        Returns:
            A user-facing response string
        """
        try:
            # Send the user's message to the AI
            response = self.llm_chat_session.send_user_message(message=message, tools=self.function_tools.get_available_tools())
            
            # Enter a loop to process function calls
            while isinstance(response, dict) and "function_tool" in response:
                # Extract function details
                function_name = response["function_tool"]
                function_args = response["function_arguments"]
                tool_call_id = response["tool_call_id"]
                
                # Execute the function
                try:
                    result = self.function_tools.execute_function(function_name, function_args)
                except Exception as e:
                    logger.error(f"Error executing function {function_name}: {e}")
        
                
                # Submit the function result back to the AI
                response = self.llm_chat_session.submit_tool_result(
                    tool_call_id=tool_call_id,
                    function_name=function_name,
                    result=result,
                    tools=self.function_tools.get_available_tools()
                )
            
            # Return the final user-facing response
            return response
            
        except Exception as e:
            logger.error(f"Error in process_message: {e}")
            return "I'm sorry, I couldn't process that request. Could you try again?"
    

    def generate_response(self, instruction: str, max_tokens: int = 100) -> str:
        """
        Generate a simple response without function calling.
        
        This is used for simple instructions like greetings.
        """
        try:
            prompt = f"{instruction.lower()}."
            response = self.llm_chat_session.send_user_message(prompt, max_tokens=max_tokens)
            return response
            
        except Exception as e:
            # Just log the error and return a default greeting for now because this function only handle send greeting now, need to change in future implementation 
            logger.error(f"Error in generate_response: {e}")
            return "Welcome to Sierra Outfitters! How can I help you today?"