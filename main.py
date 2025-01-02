import keyboard
import pyautogui
import tkinter as tk
from tkinter import ttk
import base64
from PIL import Image
from io import BytesIO
from mistralai import Mistral

# Initialize Mistral Client
API_KEY = "PxnCt3SbYET4tmdlWZin2HbCdXuqahvG"
mistral_client = Mistral(api_key=API_KEY)

# Global Variables
popup_window = None
extracted_answer = ""

def capture_screen():
    """Captures the current screen and saves it as an image."""
    screenshot_path = "screenshot.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    return screenshot_path

def convert_image_to_base64(image_path):
    """Converts an image file to a base64-encoded string."""
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        return base64.b64encode(img_data).decode("utf-8")

def process_image(image_path):
    """Processes the image using Mistral AI and extracts the response."""
    global extracted_answer
    try:
        # Convert the image to base64
        base64_image = convert_image_to_base64(image_path)
        
        # Send the base64 image to Mistral AI
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                ]
            }
        ]
        
        chat_response = mistral_client.chat.complete(
            model="pixtral-12b-2409", 
            messages=messages
        )
        source = chat_response.choices[0].message.content
        
        # Process the extracted text further
        chat_response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "try to respond to all questions in JSON format. "
                        "'REMEMBER ANSWERS FOR ALL QUESTIONS MUST BE INCLUDED IN YOUR JSON RESPONSES WITHIN 'answer' TAG', "
                        f"questions: {source}"
                    ),
                }
            ]
        )
        extracted_answer = chat_response.choices[0].message.content
        print(extracted_answer)

        # Automatically open the popup with the extracted answer
        display_popup()
    except Exception as e:
        extracted_answer = f"Error: {e}"
        print(f"Error during processing: {e}")

def display_popup():
    """Displays the extracted answer in a scrollable popup window."""
    global popup_window
    if not popup_window:
        popup_window = tk.Tk()
        popup_window.title("An Error Occured XXXXXX")
        
        # Create a frame to contain the canvas and scrollbar
        frame = tk.Frame(popup_window)
        frame.pack(fill="both", expand=True)

        # Create a canvas widget to place the content
        canvas = tk.Canvas(frame)
        canvas.pack(side="left", fill="both", expand=True)

        # Create a scrollbar for the canvas
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the content
        content_frame = tk.Frame(canvas)

        # Add the content_frame to the canvas
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Create a label with the extracted answer
        label = tk.Label(content_frame, text=extracted_answer, wraplength=400, padx=20, pady=20)
        label.pack()

        # Update the scrollable region to fit the content
        content_frame.update_idletasks()  # Make sure the content is loaded
        canvas.config(scrollregion=canvas.bbox("all"))

        # Button to close the popup
        button = tk.Button(content_frame, text="Close", command=close_popup)
        button.pack(pady=10)

        popup_window.mainloop()

def close_popup():
    """Closes the popup window."""
    global popup_window
    if popup_window:
        popup_window.destroy()
        popup_window = None

def manual_open_popup():
    """Allows the user to manually open the popup."""
    global extracted_answer
    if extracted_answer:
        print("Manually opening popup...")
        display_popup()
    else:
        print("No response available to display.")

def main():
    """Main function to handle the app flow."""
    print("App is running. Press 'q' to capture screen and process, 'p' to show popup, 'm' to close popup, and 'x' to exit.")
    
    # Listen for keyboard events
    while True:
        if keyboard.is_pressed("q"):  # Capture and process the screen
            print("Capturing screen...")
            image_path = capture_screen()
            print("Processing image...")
            process_image(image_path)
        elif keyboard.is_pressed("p"):  # Show popup manually
            print("Displaying popup manually...")
            manual_open_popup()
        elif keyboard.is_pressed("m"):  # Close popup
            print("Closing popup...")
            close_popup()
        elif keyboard.is_pressed("x"):  # Exit the app
            print("Exiting app...")
            close_popup()
            break

if __name__ == "__main__":
    main()