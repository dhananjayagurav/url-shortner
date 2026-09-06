#Base 62 encode and decode funtions 

_ALPHANUM = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE = len(_ALPHANUM)

def encode(num: int) -> str:
    result = []
    ans = str()
    if (num < 0):
        raise ValueError("Pls provide number > 0")
    
    if (num == 0):
        return _ALPHANUM[0]
    
    while (num > 0):
        num, remainder = divmod(num, _BASE)
        result.append(_ALPHANUM[remainder])
    
    ans = "".join(reversed(result))
    return ans

def decode(encode_val: str) -> int:
    if not encode_val:
        raise ValueError("cannot decode an empty string")
    num = 0
    for char in encode_val:
        index = _ALPHANUM.index(char)
        if index == -1:
            return ValueError("Invalid characters")
        num = num * _BASE + index
    return num
