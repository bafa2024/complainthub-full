# Placeholder for WhatsApp integration via Twilio or Meta API
def handle_whatsapp(request_data):
    # echo message
    incoming = request_data.get('Body')
    return "We received: " + incoming
