import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


endpoint = os.getenv("PROJECT_ENDPOINT")
model_name = os.getenv("MODEL_DEPLOYMENT")
token = os.getenv("AZURE_KEY_CREDENTIAL")  # Rename if appropriate for clarity


client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

system_message = {
    "role": "system",
    "content": "You are a helpful assistant."
}


while True:
    user_input = input("\n\nUser: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting...")
        break

    response = client.chat.completions.create(
        messages=[
            system_message,
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model=model_name,
        stream=True,
    )

    print("Assistant: ", end="", flush=True)
    for update in response:
        if update.choices and update.choices[0].delta:
            print(update.choices[0].delta.content or "", end="", flush=True)
