import datetime
import random
import webbrowser

from flask import Flask, jsonify, request, send_from_directory

try:
    import pyjokes
except ImportError:  # pragma: no cover
    pyjokes = None

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None

try:
    import wikipedia
except ImportError:  # pragma: no cover
    wikipedia = None

try:
    from pywikihow import search_wikihow
except ImportError:  # pragma: no cover
    search_wikihow = None

from views import views

app = Flask(__name__, static_folder='static')
app.register_blueprint(views, url_prefix='/views')


@app.route('/')
def frontend():
    return send_from_directory(app.root_path, 'index.html')


@app.route('/<path:filename>')
def frontend_files(filename):
    return send_from_directory(app.root_path, filename)


def handle_command(query):
    """Run a single assistant command and return the UI response text."""
    query = (query or '').strip()
    lowered = query.lower()

    if not query:
        return 'I did not hear a command.'
    if any(phrase in lowered for phrase in ('hey milo', 'hello milo', 'hi milo')):
        return 'Yes sir, how can I help?'
    if 'how are you' in lowered:
        return random.choice([
            "I'm doing well, sir. How about you?",
            "I'm great, thanks for asking!",
            'All good here, sir. How can I assist you?'
        ])
    if 'joke' in lowered:
        if pyjokes is None:
            return 'I cannot tell jokes right now because the joke library is not installed.'
        return pyjokes.get_joke()
    if 'wikipedia' in lowered:
        if wikipedia is None:
            return 'Wikipedia is not available in this environment.'
        search_query = lowered.replace('wikipedia', '').strip()
        try:
            return wikipedia.summary(search_query, sentences=2)
        except wikipedia.exceptions.DisambiguationError:
            return 'There are multiple results. Please be more specific.'
        except wikipedia.exceptions.PageError:
            return "I couldn't find that."
        except Exception:
            return "I couldn't search that right now."
    if 'open youtube' in lowered:
        webbrowser.open('https://www.youtube.com')
        return 'Sure sir, opening YouTube.'
    if 'open google' in lowered:
        webbrowser.open('https://www.google.com')
        return 'Sure sir, opening Google.'
    if 'bye bye' in lowered or 'goodbye' in lowered or lowered == 'bye':
        return 'Milo signing off, sir. See you soon.'
    return 'I am sorry sir, I did not understand that. Could you please repeat?'


def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return random.choice([
            'Good morning sir, Milo here. How can I help you?',
            'Morning sir! Milo is ready.'
        ])
    if hour < 18:
        return random.choice([
            'Good afternoon sir, Milo on duty.',
            'Good afternoon! How can I assist you?'
        ])
    return random.choice([
        'Good evening sir, what is on your mind?',
        'Evening sir! Milo is ready to help.'
    ])


def speak(audio):
    print('Milo:', audio)
    if pyttsx3 is None:
        return

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(str(audio))
        engine.runAndWait()
        engine.stop()
    except Exception:
        print('Text-to-speech is unavailable on this system.')


def takecommand():
    if sr is None:
        print('Speech recognition is not available in this environment.')
        return None

    r = sr.Recognizer()
    r.pause_threshold = 1.8
    r.non_speaking_duration = 0.5
    r.dynamic_energy_threshold = True

    speak('Listening.....')
    with sr.Microphone() as source:
        print('Listening.....')
        r.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = r.listen(source, timeout=10)
        except sr.WaitTimeoutError:
            print('No speech detected')
            off_duty = [
                'Alright sir, Milo is going off duty. See you soon.',
                "Going offline sir. I'll be here when you need me.",
                'Milo signing off sir. Have a good one.',
                'Alright sir, shutting down. See you next time.',
                'Milo is off duty sir. Until next time.',
                'Signing off sir. Take care.',
                "Alright sir, I'll be standing by until you need me again.",
                'Milo offline. Have a great day, sir.',
                "That's all for now sir. Milo signing off.",
                'Going offline now sir. See you later.'
            ]
            speak(random.choice(off_duty))
            return None

    try:
        print('Comprehending')
        speak('Comprehending')
        try:
            query = r.recognize_google(audio, language='en-IN')
        except sr.UnknownValueError:
            query = r.recognize_google(audio, language='en-US')
        print(f'user said: {query}')
        return query

    except sr.UnknownValueError:
        print('Could not understand the speech')
        speak('Could not understand the speech')
        return None
    except sr.RequestError as e:
        print('Speech service error:', e)
        speak('Speech service error')
        return None


def greeting():
    hour = int(datetime.datetime.now().hour)

    if 0 <= hour <= 12:
        morning = [
            'Good morning sir, Milo here. How can I help you?',
            'Morning sir! Milo is ready.',
            'Good morning! What can I do for you?',
            'Milo online. What are we working on today?'
        ]
        speak(random.choice(morning))
    elif 12 <= hour <= 18:
        afternoon = [
            'Good afternoon sir, Milo on duty.',
            'Good afternoon! How can I assist you?',
            'Afternoon sir! What are we working on?'
        ]
        speak(random.choice(afternoon))
    else:
        evening = [
            'Good evening sir, what is on your mind?',
            'Evening sir! Milo is ready to help.',
            'Good evening! What can I do for you?'
        ]
        speak(random.choice(evening))


def search_wikihow_result(query, max_results=1, lang='en'):
    if search_wikihow is None:
        return []
    return list(search_wikihow(query, max_results, lang))


@app.get('/api/greeting')
def greeting_response():
    return jsonify({'response': get_greeting()})


@app.post('/api/command')
def command():
    data = request.get_json(silent=True) or {}
    query = data.get('command', '')
    if not isinstance(query, str):
        return jsonify({'error': 'command must be text'}), 400

    response = handle_command(query)
    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
