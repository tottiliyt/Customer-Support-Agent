import yaml
from pathlib import Path

class SystemPromptProvider:

    _instance = None
    _prompts = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of PromptLoader exists."""
        if cls._instance is None:
            cls._instance = super(SystemPromptProvider, cls).__new__(cls)
            cls._instance._load_prompts()
        return cls._instance
    
    def _load_prompts(self) -> None:
        
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        config_path = project_root / 'config' / 'prompt.yaml'
        
        with open(config_path, 'r') as file:
            self._prompts = yaml.safe_load(file)
    
    def get_agent_prompt(self) -> str:

        return self._prompts['main_system_prompt']


