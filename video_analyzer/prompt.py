from pathlib import Path
import logging
from typing import List, Dict
import pkg_resources

logger = logging.getLogger(__name__)

class PromptLoader:
    def __init__(self, prompt_dir: str, prompts: List[Dict[str, str]]):
        # Handle user-provided prompt directory
        self.prompt_dir = Path(prompt_dir).expanduser() if prompt_dir else None
        self.prompts = prompts

    def _find_prompt_file(self, prompt_path: str) -> Path:
        """Find prompt file in user directory or package resources."""
        # If user directory specified, try both absolute and relative paths
        if self.prompt_dir:
            # Try as absolute path
            if self.prompt_dir.is_absolute():
                user_path = self.prompt_dir / prompt_path
                if user_path.exists():
                    return user_path
            else:
                # Try relative to current directory
                cwd_path = Path.cwd() / self.prompt_dir / prompt_path
                if cwd_path.exists():
                    return cwd_path
                    
                # Try relative to package root
                pkg_root = Path(__file__).parent
                pkg_path = pkg_root / self.prompt_dir / prompt_path
                if pkg_path.exists():
                    return pkg_path
            
        # Fallback to package resources
        try:
            package_path = pkg_resources.resource_filename('video_analyzer', f'prompts/{prompt_path}')
            if Path(package_path).exists():
                return Path(package_path)
        except Exception as e:
            logger.debug(f"Could not find package prompt: {e}")
            
        raise FileNotFoundError(
            f"Prompt file not found in user directory ({self.prompt_dir}) or package resources"
        )

    def get_by_index(self, index: int) -> str:
        """Load prompt from file by index.
        
        Args:
            index: Index of the prompt in the prompts list
            
        Returns:
            The prompt text content
            
        Raises:
            IndexError: If index is out of range
            FileNotFoundError: If prompt file doesn't exist
        """
        try:
            if index < 0 or index >= len(self.prompts):
                raise IndexError(f"Prompt index {index} out of range (0-{len(self.prompts)-1})")
            
            prompt = self.prompts[index]
            prompt_path = self._find_prompt_file(prompt["path"])
                
            logger.debug(f"Loading prompt '{prompt['name']}' from {prompt_path}")
            with open(prompt_path) as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading prompt at index {index}: {e}")
            raise

    def get_by_name(self, name: str) -> str:
        """Load prompt from file by name.
        
        Args:
            name: Name of the prompt to load
            
        Returns:
            The prompt text content
            
        Raises:
            ValueError: If prompt name not found
            FileNotFoundError: If prompt file doesn't exist
        """
        try:
            prompt = next((p for p in self.prompts if p["name"] == name), None)
            if prompt is None:
                raise ValueError(f"Prompt with name '{name}' not found")
            
            prompt_path = self._find_prompt_file(prompt["path"])
                
            logger.debug(f"Loading prompt '{name}' from {prompt_path}")
            with open(prompt_path) as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading prompt '{name}': {e}")
            raise
