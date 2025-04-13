from arabic_reshaper import reshape
from bidi.algorithm import get_display

def normalize_arabic(text):
    try:
        return get_display(reshape(text.strip())) if isinstance(text, str) else text
    except:
        return text
