"""Start Amicus Theologi on a random free local port and open the browser."""
import socket
import threading
import time
import webbrowser
import uvicorn

def main():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0))
        port=s.getsockname()[1]
    url=f'http://127.0.0.1:{port}'
    print(f'Amicus Theologi 0.2 läuft lokal auf {url} (Beenden mit Strg+C)')
    def open_browser():
        time.sleep(1.3)
        webbrowser.open(url)
    threading.Thread(target=open_browser,daemon=True).start()
    uvicorn.run('backend.main:app',host='127.0.0.1',port=port,log_level='warning')
if __name__=='__main__':main()
