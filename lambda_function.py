import json
import os
import openai
import boto3
from datetime import datetime

# Set your OpenAI API key as an environment variable in Lambda
openai.api_key = get_openai_api_key()  # Reads from Secrets Manager
SMARTSTUDY_MODEL = "ft:gpt-3.5-turbo-1106:your-org::smartstudy-budddy"  # Replace with your fine-tuned model name

# DynamoDB setup for context/memory storage per user
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "AlexaSmartStudyUserMemory")
table = dynamodb.Table(TABLE_NAME)

def get_user_context(user_id):
    """Retrieve user's memory/context from DynamoDB."""
    response = table.get_item(Key={"userId": user_id})
    return response.get("Item", {}).get("context", "")

def update_user_context(user_id, new_context):
    """Update user's memory/context in DynamoDB."""
    table.put_item(Item={"userId": user_id, "context": new_context})

def build_alexa_response(speech_text, should_end_session=False):
    """Helper to build Alexa JSON response."""
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech_text
            },
            "shouldEndSession": should_end_session
        }
    }

def lambda_handler(event, context):
    try:
        # Extract Alexa request details
        session = event.get('session', {})
        request = event.get('request', {})
        user_id = session.get('user', {}).get('userId', 'anonymous')
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        user_input = ""

        # Extract user utterance
        if request.get('type') == "IntentRequest":
            if "UserInput" in slots and "value" in slots["UserInput"]:
                user_input = slots["UserInput"]["value"]
            else:
                user_input = request.get("intent", {}).get("name", "")

        # Retrieve user context from DynamoDB
        previous_context = get_user_context(user_id)

        # Compose prompt for the custom model
        prompt = f"""[Previous conversation: {previous_context}]
User: {user_input}
Assistant:"""

        # Call OpenAI custom model
        response = openai.ChatCompletion.create(
            model=SMARTSTUDY_MODEL,
            messages=[
                {"role": "system", "content": "You are SmartStudy Buddy, a helpful and friendly study assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        answer = response['choices'][0]['message']['content'].strip()

        # Update context (for simplicity, append last exchange; consider truncating to fit DynamoDB size limits)
        new_context = f"{previous_context}\nUser: {user_input}\nAssistant: {answer}"
        update_user_context(user_id, new_context[-3000:])  # Keep only last 3000 chars to avoid DynamoDB size issues

        # Build Alexa response
        return build_alexa_response(answer)

    except Exception as e:
        # For debugging/logging, return a generic error
        print(f"Error: {e}")
        return build_alexa_response("Sorry, I ran into a problem. Please try again.")
