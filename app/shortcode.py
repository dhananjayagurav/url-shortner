"""Generating a shortcode is distinct responsibility. 
Keeping it different from the HTTP or storage"""

import random
import string 

_ALPHABET = string.ascii_letters + string.digits

def generate_short_code(length: int = 7) -> str:
    return "".join(random.choices(_ALPHABET, k=length))

