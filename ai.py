import ollama

def runAI(textInput: str) -> str:
    messages = [
        {"role": "system",
         "content": "helpful, knowledgable chatbot that helps people code"}
    ]
    user_message = textInput
    messages.append({"role": "user", "content": user_message})
    response = ollama.chat(
        model='llama3.2:3b', 
        messages=messages,
        options = {
            'temperature': 0.4,
            'num_ctx': 4096,
            'num_predict': 1024,
            'repeat_penalty': 1.1
        })
    ai_response = response['message']['content']
    messages.append({"role": "assistant", "content": ai_response})
    return ai_response
