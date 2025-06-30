from google import genai
from config import GEMINI_API_KEY
import random

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_mental_health_bot(user_input):
    """
    Main function to interact with the mental health chatbot
    """
    prompt = f"""
    You are MindCare AI, a compassionate and professional mental health support chatbot. You provide emotional support, active listening, and gentle guidance to users dealing with various mental health challenges.

    IMPORTANT GUIDELINES:
    - Be empathetic, non-judgmental, and supportive
    - Use warm, caring language while maintaining professionalism
    - Provide practical coping strategies and techniques
    - Encourage self-reflection and positive thinking
    - NEVER provide medical diagnoses or replace professional therapy
    - If someone mentions self-harm or suicidal thoughts, gently encourage them to seek immediate professional help
    - Focus on emotional validation and practical mental wellness tips
    - Ask follow-up questions to better understand their situation
    - Keep responses conversational but helpful (2-4 paragraphs)

    User's message: {user_input}

    Respond with empathy and provide supportive guidance. If appropriate, offer specific coping techniques or mindfulness exercises.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting right now. Please try again in a moment. In the meantime, remember that you're not alone, and it's okay to reach out for support. 💙"

def generate_wellness_tips(user_profile=None):
    """
    Generate personalized wellness tips based on user profile
    """
    base_prompt = """
    You are a mental wellness coach. Generate 5-7 practical, actionable mental health and wellness tips that can be implemented daily. 
    
    Focus on:
    - Stress management techniques
    - Mindfulness and meditation practices
    - Healthy lifestyle habits for mental well-being
    - Social connection and relationship building
    - Self-care practices
    - Cognitive behavioral strategies
    
    Make the tips specific, practical, and easy to follow. Format them as a numbered list with brief explanations.
    """
    
    if user_profile:
        profile_context = f"""
        Consider this user profile when generating tips:
        - Age: {user_profile.get('age', 'Not specified')}
        - Occupation: {user_profile.get('occupation', 'Not specified')}
        - Stress Level: {user_profile.get('stress_level', 'Not specified')}
        - Mental Health Concerns: {user_profile.get('mental_health_concerns', 'Not specified')}
        - Support Preferences: {user_profile.get('support_preferences', 'Not specified')}
        
        Tailor the tips to be relevant to their specific situation and preferences.
        """
        prompt = base_prompt + profile_context
    else:
        prompt = base_prompt
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return get_fallback_tips()

def generate_mood_insights(mood_data):
    """
    Generate insights based on mood tracking data
    """
    if not mood_data or len(mood_data) < 3:
        return "Keep tracking your mood for a few more days to get personalized insights! 📈"
    
    # Calculate averages
    avg_mood = sum([entry['mood_scale'] for entry in mood_data]) / len(mood_data)
    avg_energy = sum([entry['energy_level'] for entry in mood_data]) / len(mood_data)
    avg_anxiety = sum([entry['anxiety_level'] for entry in mood_data]) / len(mood_data)
    avg_sleep = sum([entry['sleep_quality'] for entry in mood_data]) / len(mood_data)
    
    prompt = f"""
    You are a mental wellness analyst. Based on the following mood tracking data, provide gentle, supportive insights and suggestions:

    Mood Tracking Summary (last {len(mood_data)} entries):
    - Average Mood: {avg_mood:.1f}/10
    - Average Energy: {avg_energy:.1f}/10  
    - Average Anxiety: {avg_anxiety:.1f}/10
    - Average Sleep Quality: {avg_sleep:.1f}/10

    Recent mood patterns and any notes from entries should be considered.

    Provide:
    1. A brief, encouraging assessment of their patterns
    2. 2-3 specific, actionable suggestions for improvement
    3. Recognition of positive trends if any
    4. Gentle recommendations for areas that need attention

    Keep the tone supportive, non-judgmental, and hopeful. Avoid medical terminology or diagnoses.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return get_fallback_insights(avg_mood, avg_energy, avg_anxiety, avg_sleep)

def generate_journal_reflection(journal_entry):
    """
    Provide gentle reflection and insights on journal entries
    """
    prompt = f"""
    You are a supportive mental health companion. The user has shared a journal entry with you. Provide a thoughtful, empathetic response that:

    1. Acknowledges their feelings and experiences
    2. Highlights any positive aspects or growth you notice
    3. Offers gentle insights or alternative perspectives if appropriate
    4. Suggests one practical coping strategy or reflection question
    5. Encourages continued journaling and self-reflection

    Journal Entry: {journal_entry}

    Respond with warmth and understanding, as if you're a caring friend who's really listening. Keep your response 2-3 paragraphs, focused on support and gentle guidance.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "Thank you for sharing your thoughts with me. Journaling is such a powerful tool for self-reflection and emotional processing. Keep writing and being honest with yourself - you're doing great work in understanding your inner world. 💙"

def get_daily_affirmation():
    """
    Get a daily positive affirmation
    """
    affirmations = [
        "You are stronger than you think and more resilient than you know. 🌟",
        "Every small step forward is progress worth celebrating. 🎉",
        "Your feelings are valid, and it's okay to take things one day at a time. 🌅",
        "You have survived 100% of your difficult days so far - that's an amazing track record. 💪",
        "Self-compassion is not selfish; it's necessary for your well-being. 💙",
        "You are worthy of love, kindness, and all good things in life. ✨",
        "It's okay to not be okay sometimes. Healing isn't linear. 🌱",
        "You are making a difference simply by being here and trying. 🌈",
        "Your mental health matters, and taking care of it is a sign of strength. 🧠💚",
        "Tomorrow is a new day with new possibilities and fresh hope. 🌄"
    ]
    
    return random.choice(affirmations)

def get_breathing_exercise():
    """
    Provide a simple breathing exercise
    """
    exercises = [
        """
        **4-7-8 Breathing Exercise:**
        1. Exhale completely through your mouth
        2. Inhale through your nose for 4 counts
        3. Hold your breath for 7 counts  
        4. Exhale through your mouth for 8 counts
        5. Repeat 3-4 times
        
        This helps activate your body's relaxation response. 🌸
        """,
        """
        **Box Breathing:**
        1. Inhale for 4 counts
        2. Hold for 4 counts
        3. Exhale for 4 counts
        4. Hold empty for 4 counts
        5. Repeat 5-10 times
        
        Great for reducing anxiety and improving focus. 📦✨
        """,
        """
        **5-5 Calming Breath:**
        1. Breathe in slowly for 5 counts
        2. Breathe out slowly for 5 counts
        3. Focus on making your exhale slightly longer
        4. Continue for 2-3 minutes
        
        Perfect for moments when you need quick centering. 🧘‍♀️
        """
    ]
    
    return random.choice(exercises)

def get_fallback_tips():
    """
    Fallback wellness tips when AI is unavailable
    """
    return """
    Here are some essential mental wellness tips:
    
    1. **Practice Mindful Breathing** - Take 5 deep breaths when feeling overwhelmed
    2. **Stay Connected** - Reach out to a friend or family member regularly  
    3. **Move Your Body** - Even a 10-minute walk can improve your mood
    4. **Limit Social Media** - Set boundaries on screen time for better mental health
    5. **Practice Gratitude** - Write down 3 things you're grateful for each day
    6. **Prioritize Sleep** - Aim for 7-9 hours of quality sleep nightly
    7. **Be Kind to Yourself** - Treat yourself with the same compassion you'd show a good friend
    """

def get_fallback_insights(avg_mood, avg_energy, avg_anxiety, avg_sleep):
    """
    Fallback insights when AI is unavailable
    """
    insights = []
    
    if avg_mood >= 7:
        insights.append("Your mood levels look positive overall - keep up whatever you're doing! 🌟")
    elif avg_mood >= 5:
        insights.append("Your mood is in a balanced range. Consider small daily practices to boost it further.")
    else:
        insights.append("I notice your mood has been lower lately. Remember, it's okay to have difficult periods.")
    
    if avg_sleep < 5:
        insights.append("Your sleep quality could use some attention - good sleep is crucial for mental wellness.")
    
    if avg_anxiety > 7:
        insights.append("Your anxiety levels seem elevated. Consider practicing relaxation techniques daily.")
    
    return " ".join(insights) + "\n\nRemember, you're doing great by tracking and being aware of your patterns. 💙"