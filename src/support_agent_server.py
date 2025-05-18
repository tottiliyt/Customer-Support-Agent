from pathlib import Path
from openai import OpenAI

from agent.support_agent import SupportAgent
from tools.check_promotion_eligibility import CheckPromotionEligibility
from tools.function_tools import FunctionTools
from agent.system_prompt_provider import SystemPromptProvider
from agent.llm_chat_session import LLMChatSession
from store.order_store import OrderStore
from store.product_embedding_store import ProductEmbeddingStore
from store.product_store import ProductStore
from tools.lookup_order import LookUpOrder
from tools.recommend_product import RecommendProduct
from utils.logger import logger

class SupportAgentServer:
    _instance = None
    
    def __new__(cls, openai_api_key: str, project_root: Path):
        """Singleton pattern to ensure only one instance of SupportAgentServer exists."""
        if cls._instance is None:
            cls._instance = super(SupportAgentServer, cls).__new__(cls)
            cls._instance._initialize(openai_api_key, project_root)
        return cls._instance
    
    def _initialize(self, openai_api_key: str, project_root: Path):
        data_dir = project_root / 'data'
        openai_client = OpenAI(api_key=openai_api_key)

        product_store = ProductStore(data_dir / 'ProductCatalog.json')
        product_embedding_store = ProductEmbeddingStore(product_store, data_dir / 'ProductEmbeddings.json')
        order_store = OrderStore(data_dir / 'CustomerOrders.json')
        system_prompt_provider = SystemPromptProvider()
        
        lookup_order = LookUpOrder(order_store)
        check_promotion_eligibility = CheckPromotionEligibility()
        recommend_product = RecommendProduct(product_embedding_store, product_store)
        
        function_tools = FunctionTools([lookup_order, check_promotion_eligibility, recommend_product])
        
        self.conversation_manager = SupportAgent(system_prompt_provider, function_tools, openai_client)

    def start(self):
        # Agent start to chat with user
        print("\n\nSierra Outfitters Customer Support Agent")
        
        try:
            # Generate greeting
            greeting = self.conversation_manager.generate_response("send a greeting to user")
            print(f"\n\n🤖 Assistant: {greeting}")

            # Main conversation loop
            while True:
                user_input = input("\n\n👤 You: ")
                response = self.conversation_manager.process_message(user_input)
                print(f"\n\n🤖 Assistant: {response}")

        except KeyboardInterrupt:
            print("\n\nExiting customer support agent. Goodbye!")
        except Exception as e:
            # This should rarely happen since errors are handled in SupportAgent
            logger.error(f"Critical error in main loop: {e}")
            print(f"\n\n❌ Error: The customer support agent encountered an error and needs to close.")
            print("Please restart the application.")
            return
