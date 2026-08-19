"""
storage_logic.py

Provides the logic for the Universal Message Sorter to dynamically
create folders and save sorted text files to the precise categories on the disk.
"""
import os
from config import MESSAGES_DIR, ensure_app_directories

def save_message_to_folder(category: str, filename: str, content: str) -> str:
    """
    Saves a text message into a specific categorized folder.
    Creates the folder automatically if it doesn't exist.
    """
    ensure_app_directories()
    base_dir = str(MESSAGES_DIR)
    
    # Secure the category path to prevent directory traversal attacks
    clean_category = category.replace("..", "").replace("/", "_").strip()
    clean_filename = filename.replace("..", "").replace("/", "_").strip()
    
    if not clean_filename.endswith('.txt'):
        clean_filename += '.txt'
        
    target_dir = os.path.join(base_dir, clean_category)
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, clean_filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"✅ Successfully saved message to: {file_path}"
    except Exception as e:
        return f"❌ Failed to save message: {str(e)}"
