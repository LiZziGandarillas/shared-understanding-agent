"""
Clarification Engine — MVP module.

Decides what to ask next. Compares the current Shared Understanding
Model against the minimum thresholds and generates the next question
for the least-covered category.

Input: current Shared Understanding Model + conversation history.
Output: next question tagged by category, or a "covered" signal.
Depends on: Shared Understanding Model, Bedrock.
Feeds into: Conversation Engine.
"""
