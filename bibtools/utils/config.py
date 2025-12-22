"""Configuration loader for API keys and credentials."""

import os
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Optional[Path] = None) -> dict[str, str]:
    """Load environment variables from .env.local file.
    
    Args:
        env_path: Path to .env file. If None, searches for .env.local in project root.
        
    Returns:
        Dictionary of environment variables
    """
    if env_path is None:
        # Search for .env.local in project root (2 levels up from this file)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        env_path = project_root / '.env.local'
    
    env_vars = {}
    
    if not env_path.exists():
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def get_zotero_config() -> dict[str, str]:
    """Get Zotero API configuration.
    
    Returns:
        Dictionary with api_key, library_id, library_type
    """
    env_vars = load_env_file()
    
    return {
        'api_key': env_vars.get('ZOTERO_API_KEY', ''),
        'library_id': env_vars.get('ZOTERO_LIBRARY_ID', ''),
        'library_type': env_vars.get('ZOTERO_LIBRARY_TYPE', 'group'),
    }


def get_springer_api_key() -> str:
    """Get Springer API key.
    
    Returns:
        Springer API key string
    """
    env_vars = load_env_file()
    return env_vars.get('SPRINGER_API_KEY', '')
