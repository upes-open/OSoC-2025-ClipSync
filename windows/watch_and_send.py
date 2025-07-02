import pyperclip
import time
import traceback

def monitor_clipboard(interval=1):
    last_text = ""
    
    print("Monitoring clipboard for changes. Press Ctrl+C to stop.")
    
    try:
        while True:
            try:
                current_text = pyperclip.paste()
            except Exception as e:
                print(f"[Error accessing clipboard]: {e}")
                traceback.print_exc()
                time.sleep(interval)
                continue  

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
    Clean or format text before sending (e.g., trimming whitespace).
    """
    return text.strip()

if __name__ == "__main__":
    monitor_clipboard(interval=1)
