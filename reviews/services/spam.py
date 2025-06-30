import os
import requests

SPAM_URL = os.getenv("SPAM_DETECTOR_URL") 
SPAM_API_KEY = os.getenv("SPAM_API_KEY")

def check_for_spam(text):
    """
    Check if text is spam using external spam detection API
    Returns: (is_spam, spam_probability, non_spam_probability)
    Always returns valid values even if API is unavailable
    """
    if not SPAM_URL or not SPAM_API_KEY:
        print("Spam detection API not configured")
        return False, 0.0, 1.0
    
    try:
        headers = {"X-API-KEY": f"{SPAM_API_KEY}"}
        payload = {"text": text}
        
        print(f"Spam detection request: URL={SPAM_URL}, Headers={headers}, Payload={payload}")
        
        response = requests.post(
            SPAM_URL,
            json=payload,
            headers=headers,
            timeout=10  
        )
        
        print(f"Spam detection response: Status={response.status_code}, Headers={response.headers}")
        
        response.raise_for_status()
        data = response.json()
        
        print(f"Spam detection result: {data}")
        
        is_spam = bool(data.get("is_spam", False))
        spam_probability = float(data.get("spam_probability", 0.0))
        non_spam_probability = float(data.get("non_spam_probability", 1.0))
        
        if spam_probability < 0 or spam_probability > 1:
            spam_probability = 0.0
        if non_spam_probability < 0 or non_spam_probability > 1:
            non_spam_probability = 1.0
            
        return is_spam, spam_probability, non_spam_probability
        
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Spam detection API error: {e}")
        return False, 0.0, 1.0
    except Exception as e:
        print(f"Unexpected error in spam detection: {e}")
        return False, 0.0, 1.0
