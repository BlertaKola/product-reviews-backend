import os
import requests
from ..utils import log_ai_error

SPAM_URL = os.getenv("SPAM_DETECTOR_URL") 

def check_for_spam(text):
    """
    Check if text is spam using external spam detection API
    Returns: (is_spam, spam_probability, non_spam_probability)
    Always returns valid values even if API is unavailable
    """
    if not SPAM_URL:
        print("Spam detection API not configured")
        return False, 0.0, 1.0
    
    try:
        payload = {"text": text}
        
        print(f"Spam detection request: URL={SPAM_URL}, Payload={payload}")
        
        response = requests.post(
            SPAM_URL,
            json=payload,
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
        
    except requests.RequestException as e:
        status_code = None
        if hasattr(e, 'response') and e.response:
            status_code = e.response.status_code
        log_ai_error('spam_detection', text, e, status_code=status_code)
        return False, 0.0, 1.0
        
    except (ValueError, KeyError) as e:
        log_ai_error('spam_detection', text, f"Data parsing error: {e}")
        return False, 0.0, 1.0
        
    except Exception as e:
        log_ai_error('spam_detection', text, f"Unexpected error: {e}")
        return False, 0.0, 1.0
