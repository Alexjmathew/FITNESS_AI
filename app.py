from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Fitness-specific system prompt
FITNESS_SYSTEM_PROMPT = """
You are FitBot, a knowledgeable and friendly fitness assistant. Your expertise includes:
- Exercise routines and workout plans
- Nutrition advice and meal planning
- Weight loss and muscle gain strategies
- Proper form and technique for exercises
- Fitness tracking and goal setting
- Recovery and injury prevention

Always provide safe, evidence-based advice and encourage users to consult with healthcare professionals for medical concerns.
Keep responses clear, practical, and motivational.
"""

class FitnessChatbot:
    def __init__(self):
        self.conversation_history = []
    
    def get_response(self, user_message):
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Prepare messages for OpenAI (system prompt + conversation history)
            messages = [
                {"role": "system", "content": FITNESS_SYSTEM_PROMPT}
            ] + self.conversation_history[-6:]  # Keep last 6 messages for context
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content.strip()
            
            # Add bot response to conversation history
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}"

# Initialize chatbot
chatbot = FitnessChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        
        if not user_message.strip():
            return jsonify({'response': 'Please enter a message.'})
        
        # Get response from chatbot
        bot_response = chatbot.get_response(user_message)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'response': f'Sorry, an error occurred: {str(e)}',
            'status': 'error'
        })

@app.route('/clear', methods=['POST'])
def clear_chat():
    chatbot.conversation_history.clear()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
