from twilio.twiml.voice_response import VoiceResponse
from fastapi import HTTPException

class TwilioVoiceAdapter:
    @staticmethod
    def handle_call(request_data):
        # generate TwiML (basic)
        resp = VoiceResponse()
        resp.say("Hello, please state your complaint after the beep.")
        resp.record(timeout=5, transcribe=True, transcribe_callback='/api/v1/webhook/voice/twilio')
        return str(resp)
