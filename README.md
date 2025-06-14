# Smart Study Buddy

This project integrates a custom OpenAI model ("SmartStudy Buddy") with Alexa Skills using AWS Lambda and DynamoDB for user-specific memory/context.

## Features

- Uses a fine-tuned OpenAI GPT model for study assistance.
- Alexa skill integration via AWS Lambda.
- Contextual, personalized conversations per user (stored in DynamoDB).

## Setup

1. **Create DynamoDB Table:**  
   - Table name: `AlexaSmartStudyUserMemory`
   - Partition key: `userId` (String)

2. **Deploy Lambda:**  
   - Set environment variables:
     - `OPENAI_API_KEY`
     - `DYNAMODB_TABLE` (default: `AlexaSmartStudyUserMemory`)
   - Add the `lambda_function.py` code.

3. **Configure Alexa Skill:**  
   - Point the skill endpoint to this Lambda.
   - Use a slot named `UserInput` for free-form input.

> Replace the `SMARTSTUDY_MODEL` variable in the code with your actual fine-tuned OpenAI model name.
