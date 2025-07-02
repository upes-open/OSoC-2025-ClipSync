import pyperclip
import time

def monitor_clipboard(interval=1):
    last_text = ""
    
    print("Monitoring clipboard for changes. Press Ctrl+C to stop.")
    
    try:
        while True:
            current_text = pyperclip.paste()
            
            if current_text != last_text:
                last_text = current_text
                print("\n[Clipboard Updated]")
                prepared_text = prepare_text(current_text)
                print("Prepared Text for Sending:", prepared_text)
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\nStopped clipboard monitoring.")

def prepare_text(text):
    """
    Placeholder function to clean or format text before sending.
    You can modify this based on your needs.
    """
    return text.strip()

if __name__ == "__main__":
    monitor_clipboard(interval=1)  
