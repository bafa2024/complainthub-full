# Placeholder for Telegram Bot integration
def handle_telegram(request_data):
    message = request_data.get('message', {}).get('text')
    return "You said: " + message
