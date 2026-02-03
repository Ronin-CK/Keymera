import abc
import os
import json
import asyncio
import re
import aiohttp
import random
import time
import hashlib
from typing import Optional, List, Dict, Any
import google.generativeai as genai

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_INSTRUCTION = """You are Keymera, a text TRANSFORMATION engine. You TRANSFORM input text, you do NOT reply to it.

CRITICAL: You are NOT having a conversation. You REWRITE/TRANSFORM the given text.

ABSOLUTE RULES:
1. Output ONLY the transformed text - nothing else
2. NEVER respond TO the text as if it's a message to you
3. NEVER start with "Here is", "Sure!", "Certainly!", "Of course", etc.
4. NEVER wrap output in quotation marks unless the style requires it
5. NEVER use markdown formatting (no **, no ```, no #) unless specifically requested
6. NEVER explain or add commentary
7. Start IMMEDIATELY with the transformed result
8. Preserve the original meaning unless the style specifically requires changing it

Example - Transform "gonna be late" to formal:
INPUT: gonna be late
WRONG: "I understand you'll be late. Where are you?"  ← This is RESPONDING, not transforming!
CORRECT: I will be arriving late.  ← This is TRANSFORMING the input"""

VARIATION_PROMPTS = [
    "Use COMPLETELY different vocabulary - no words from typical responses.",
    "Start with a different word than usual. Be creative with sentence structure.",
    "Rephrase using synonyms and a fresh sentence pattern.",
    "Express this in an unexpected but appropriate way.",
    "Use a different tone variation while keeping the style.",
    "Restructure the sentence entirely - different word order.",
    "Be more creative than the obvious answer.",
    "Find an alternative phrasing that's equally valid.",
    "Use less common but appropriate vocabulary.",
    "Take a slightly different angle on expressing this.",
]
