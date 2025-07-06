import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.core.clipboard import Clipboard

# Required for Android (will not run on desktop)
try:
    from android.permissions import request_permissions, Permission
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, PythonJavaClass, java_method
    from android import activity
    
    # Android classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    WindowManager = autoclass('android.view.WindowManager')
    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    
    ANDROID_AVAILABLE = True
except ImportError:
    Logger.warning("ClipSync: Android modules not available. Running in desktop mode.")
    ANDROID_AVAILABLE = False


class FloatingClipboardWidget(FloatLayout):
    """
    A floating widget that monitors clipboard content and stays visible
    to maintain focus for Android v10+ compatibility
    """
    
    def __init__(self, **kwargs):
        super(FloatingClipboardWidget, self).__init__(**kwargs)
        
        # Last known clipboard content
        self.last_clipboard_content = ""
        
        # Flag to track if we're actively monitoring
        self.is_monitoring = False
        
        # Setup the UI
        self.setup_ui()
        
        # Request necessary permissions on Android
        if ANDROID_AVAILABLE:
            self.request_android_permissions()
    
    def setup_ui(self):
        """Setup the floating UI components"""
        
        # Main container with semi-transparent background
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=5,
            padding=10,
            size_hint=(None, None),
            size=(200, 120),
            pos_hint={'x': 0.8, 'y': 0.8}  # Position in top-right corner
        )
        
        # Status label
        self.status_label = Label(
            text='ClipSync Ready',
            size_hint_y=0.4,
            font_size='12sp',
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        
        # Clipboard content preview (truncated)
        self.clipboard_preview = Label(
            text='Clipboard: Empty',
            size_hint_y=0.4,
            font_size='10sp',
            halign='center',
            valign='middle',
            text_size=(180, None)
        )
        
        # Control button
        self.control_button = Button(
            text='Start Monitoring',
            size_hint_y=0.2,
            font_size='11sp'
        )
        self.control_button.bind(on_press=self.toggle_monitoring)
        
        # Add widgets to layout
        main_layout.add_widget(self.status_label)
        main_layout.add_widget(self.clipboard_preview)
        main_layout.add_widget(self.control_button)
        
        # Add semi-transparent background
        with main_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 0.7)  # Semi-transparent black
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        # Bind size and position updates
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        """Update background rectangle size and position"""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def request_android_permissions(self):
        """Request necessary Android permissions"""
        if not ANDROID_AVAILABLE:
            return
            
        # Request permissions that might be needed
        permissions = [
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
        ]
        
        try:
            request_permissions(permissions)
            Logger.info("ClipSync: Android permissions requested")
        except Exception as e:
            Logger.error(f"ClipSync: Error requesting permissions: {e}")
    
    def toggle_monitoring(self, instance):
        """Toggle clipboard monitoring on/off"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring clipboard content"""
        self.is_monitoring = True
        self.control_button.text = 'Stop Monitoring'
        self.status_label.text = 'Monitoring Active'
        
        # Schedule periodic clipboard checks
        Clock.schedule_interval(self.check_clipboard, 0.5)  # Check every 500ms
        
        Logger.info("ClipSync: Started clipboard monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring clipboard content"""
        self.is_monitoring = False
        self.control_button.text = 'Start Monitoring'
        self.status_label.text = 'Monitoring Stopped'
        
        # Unschedule clipboard checks
        Clock.unschedule(self.check_clipboard)
        
        Logger.info("ClipSync: Stopped clipboard monitoring")
    
    def check_clipboard(self, dt):
        """Check clipboard content for changes"""
        try:
            # Get current clipboard content
            current_content = Clipboard.paste()
            
            # Check if content has changed
            if current_content != self.last_clipboard_content:
                self.on_clipboard_changed(current_content)
                self.last_clipboard_content = current_content
                
        except Exception as e:
            Logger.error(f"ClipSync: Error checking clipboard: {e}")
            self.status_label.text = 'Error reading clipboard'
    
    def on_clipboard_changed(self, new_content):
        """Handle clipboard content changes"""
        # Update preview (truncate long content)
        preview_text = new_content[:30] + "..." if len(new_content) > 30 else new_content
        preview_text = preview_text.replace('\n', ' ')  # Remove newlines for display
        
        self.clipboard_preview.text = f'Clipboard: {preview_text}'
        self.status_label.text = f'Content detected ({len(new_content)} chars)'
        
        Logger.info(f"ClipSync: Clipboard changed - {len(new_content)} characters")
        
        # in the next function we send data to the other devices , ( currently just logging)
        self.process_clipboard_content(new_content)
    
    def process_clipboard_content(self, content):
        """Process the clipboard content (placeholder for sync logic)"""
        # placeholder for syncing logic
        
        Logger.info(f"ClipSync: Processing clipboard content: {content[:50]}...")
        
        # Placeholder - in future we will add :
        # 1. Encrypt the content using your AES crypto
        # 2. Send it to configured devices
        # 3. Handle any network errors


class ClipSyncFloatingApp(App):
    """
    Main Kivy application that creates a floating, persistent clipboard monitor
    """
    
    def build(self):
        """Build the application"""
        # Set window properties for floating behavior
        if ANDROID_AVAILABLE:
            self.setup_android_floating_window()
        else:
            # Desktop mode - smaller window for testing
            Window.size = (300, 150)
            Window.always_on_top = True
        
        # Create and return the main widget
        self.floating_widget = FloatingClipboardWidget()
        return self.floating_widget
    
    def setup_android_floating_window(self):
        """Setup Android-specific floating window properties"""
        try:
            # This would be used for system overlay windows
            # Note: Requires SYSTEM_ALERT_WINDOW permission for true floating
            Logger.info("ClipSync: Setting up Android floating window")
            
            # For now, we'll use a regular window that stays in focus
            # In a production app, you might want to implement a proper overlay
            
        except Exception as e:
            Logger.error(f"ClipSync: Error setting up Android floating window: {e}")
    
    def on_start(self):
        """Called when the application starts"""
        Logger.info("ClipSync: Application started")
        
        # Keep the app in focus to maintain clipboard access
        if ANDROID_AVAILABLE:
            self.maintain_focus()
    
    def maintain_focus(self):
        """Maintain application focus for clipboard access"""
        try:
            # Schedule periodic focus maintenance
            Clock.schedule_interval(self.focus_maintenance, 1.0)  # Every second
        except Exception as e:
            Logger.error(f"ClipSync: Error maintaining focus: {e}")
    
    def focus_maintenance(self, dt):
        """Periodic focus maintenance"""
        # This helps ensure the app stays in focus
        # Additional focus maintenance logic can be added here
        pass
    
    def on_pause(self):
        """Called when the app is paused"""
        Logger.info("ClipSync: Application paused")
        # Return True to keep the app running in background
        return True
    
    def on_resume(self):
        """Called when the app is resumed"""
        Logger.info("ClipSync: Application resumed")


def main():
    """Main entry point"""
    try:
        # Create and run the floating clipboard app
        app = ClipSyncFloatingApp()
        app.run()
    except Exception as e:
        Logger.error(f"ClipSync: Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()