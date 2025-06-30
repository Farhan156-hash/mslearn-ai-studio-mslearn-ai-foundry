import os
import tkinter as tk
from tkinter import scrolledtext, font
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "gray"
        self.default_color = "black"
        
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure OpenAI Chat")
        self.root.geometry("800x650")
        self.root.configure(bg="#f5f5f5")
        
        # Custom fonts
        self.title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.message_font = font.Font(family="Segoe UI", size=11)
        self.input_font = font.Font(family="Segoe UI", size=12)
        
        # Header frame
        header_frame = tk.Frame(root, bg="#4b8bbe")
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        header_label = tk.Label(
            header_frame,
            text="Azure OpenAI Chat Assistant",
            font=self.title_font,
            bg="#4b8bbe",
            fg="white",
            padx=20,
            pady=15
        )
        header_label.pack(side=tk.LEFT)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state='disabled',
            bg="white",
            fg="#333333",
            font=self.message_font,
            padx=15,
            pady=15,
            relief=tk.FLAT
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 5))
        
        # Input frame
        input_frame = tk.Frame(root, bg="#f5f5f5")
        input_frame.pack(fill=tk.X, padx=20, pady=(5, 20))
        
        # Input field with placeholder
        self.user_input = PlaceholderEntry(
            input_frame,
            placeholder="Type your message here...",
            font=self.input_font,
            relief=tk.GROOVE,
            bd=2
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)
        
        # Attractive send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
            font=self.input_font,
            activebackground="#45a049",
            relief=tk.RAISED,
            bd=0,
            padx=20,
            pady=8
        )
        self.send_button.pack(side=tk.RIGHT)
        
        self.init_azure_clients()

    def init_azure_clients(self):
        try:
            load_dotenv()
            project_connection = os.getenv("PROJECT_ENDPOINT")
            model_deployment = os.getenv("MODEL_DEPLOYMENT")
            azure_key_credential = os.getenv("AZURE_KEY_CREDENTIAL")

            self.chat_client = ChatCompletionsClient(
                endpoint=project_connection,
                credential=AzureKeyCredential(azure_key_credential),
            )

            self.model_deployment = model_deployment
            self.prompt = [SystemMessage("You are a helpful AI assistant that answers questions.")]
            self.display_message("System", "Chat initialized with Azure OpenAI")

        except Exception as e:
            self.display_message("System", f"Error initializing Azure clients: {e}", error=True)

    def send_message(self, event=None):
        user_text = self.user_input.get()
        if user_text == "Type your message here..." or not user_text.strip():
            return

        self.display_message("You", user_text)
        self.prompt.append(UserMessage(user_text))
        self.user_input.delete(0, tk.END)
        
        try:
            # Show typing indicator
            typing_id = self.display_message("Assistant", "Thinking...", temp=True)
            
            response = self.chat_client.complete(
                model=self.model_deployment,
                messages=self.prompt
            )
            completion = response.choices[0].message.content
            
            # Remove typing indicator and add actual response
            self.chat_display.config(state='normal')
            self.chat_display.delete(typing_id, tk.END)
            self.chat_display.insert(tk.END, f"Assistant: {completion}\n\n", "assistant")
            self.chat_display.tag_config("assistant", foreground="#0066cc")
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)
            
            self.prompt.append(AssistantMessage(completion))
        except Exception as e:
            self.display_message("System", f"Error: {e}", error=True)

    def display_message(self, sender, message, error=False, temp=False):
        self.chat_display.config(state='normal')
        
        tag = "error" if error else sender.lower()
        fg_color = "#cc0000" if error else ("#0066cc" if sender == "Assistant" else "#333333")
        
        self.chat_display.tag_config(tag, foreground=fg_color)
        pos = self.chat_display.index(tk.END)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n", tag)
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
        return pos if temp else None

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
