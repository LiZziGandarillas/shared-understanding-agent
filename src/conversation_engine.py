"""
Conversation Engine — MVP module.

Manages the dialogue turn: receives the initial problem statement,
maintains conversation history, sends each turn to Bedrock, and
receives the next clarifying question or synthesis.

Input: initial statement + user responses per turn.
Output: structured history (role, text, timestamp).
Depends on: Bedrock.
Feeds into: Clarification Engine, Shared Understanding Model.
"""
