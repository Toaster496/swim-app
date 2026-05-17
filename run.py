from swimapp import create_app
import os
import sys
import webbrowser
import threading

def open_browser():
    """Open browser after server starts"""
    import time
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    app = create_app()
    
    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the Flask app
    app.run(host='127.0.0.1', port=5000, debug=False)
