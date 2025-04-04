import openai
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
THREAD_ID = os.getenv('OPENAI_THREAD_ID')

def get_rating_and_report_from_file(file_path):
    try:
        print(f"Starting analysis for file: {file_path}")

        # Upload the file
        try:
            with open(file_path, "rb") as f:
                uploaded_file = openai.files.create(
                    file=f,
                    purpose="assistants"
                )
            print(f"File uploaded with ID: {uploaded_file.id}")
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

        # Create a user message
        try:
            print("Creating user message...")
            user_message = openai.beta.threads.messages.create(
                thread_id=THREAD_ID,
                role="user",
                content="Please analyze this document and return a JSON object with keys: rating (1-5), and report (a short parent-friendly summary).",
                attachments=[{
                    "file_id": uploaded_file.id,
                     "tools": [{"type": "file_search"}]
                }]
            )

            print(f"User message created with ID: {user_message.id}")
        except Exception as e:
            print(f"Error creating user message: {e}")
            return None

        # Start the assistant run
        try:
            assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
            print(f"Starting run with assistant ID: {assistant_id}")
            run = openai.beta.threads.runs.create(
                thread_id=THREAD_ID,
                assistant_id=assistant_id
            )
            print(f"Run started with ID: {run.id}")
        except Exception as e:
            print(f"Error starting run: {e}")
            return None

        # Poll for run completion
        try:
            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=THREAD_ID, run_id=run.id)
                print(f"Run status: {run_status.status}")
                if run_status.status == "completed":
                    print("Run completed successfully.")
                    break
                elif run_status.status in ["failed", "cancelled"]:
                    raise Exception(f"Run failed or cancelled: {run_status.status}")
                print("Waiting for run to complete...")
                time.sleep(2)
        except Exception as e:
            print(f"Error during run polling: {e}")
            return None

        # Retrieve messages
        try:
            print("Retrieving messages...")
            messages = openai.beta.threads.messages.list(thread_id=THREAD_ID)
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    raw_response = msg.content[0].text.value
                    print("\nAssistant's Response (raw):\n")
                    print(raw_response)
                    try:
                        parsed = json.loads(raw_response)
                        return parsed
                    except json.JSONDecodeError:
                        print("Failed to parse JSON.")
                        return None
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return None

        print("No valid response from assistant.")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    result = get_rating_and_report_from_file("example.pdf")
    if result:
        print("\nFinal Result:\n")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to get a valid result.")

