"""
social_logic.py

Provides mock/read-only tools for interacting with Twitter and Instagram.
Currently safely mocks the data to prevent bot detection on real accounts.
"""

def check_twitter_dms() -> str:
    """Mock checking Twitter Direct Messages."""
    return "🐦 [Twitter Mock]: You have 1 new DM from @tech_news: 'Check out the new AI update!'"

def check_instagram_dms() -> str:
    """Mock checking Instagram Direct Messages."""
    return "📷 [Instagram Mock]: No new direct messages. You have 2 new likes on your recent post."
