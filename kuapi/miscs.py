from urllib.parse import parse_qs

def satinize(text: str):
    return text.strip() if text else None

def extract_query_from_url(url:str, keys:tuple):
    r = parse_qs(url)
    result = dict()

    for k in keys:
        result.setdefault(k, r.get(k)[0])
    return result