"""Amicus Theologi Windows desktop launcher.

A small local control window owns the HTTP server lifetime. The browser is merely
its document frontend; closing the browser alone does not lose user data.
No administrator privileges, external connections or Python installation needed
when bundled with PyInstaller.
"""
from __future__ import annotations

import logging
import os
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

# When launched via `python windows/launcher.py`, include the repository root.
# PyInstaller bundles these same imports, and `--paths .` lets its analyzer find them.
if getattr(sys, 'frozen', False) and os.name == 'nt':
    # PyInstaller --windowed can provide no stdout/stderr streams.
    if sys.stdout is None:sys.stdout=open(os.devnull,'w',encoding='utf-8')
    if sys.stderr is None:sys.stderr=open(os.devnull,'w',encoding='utf-8')
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from backend.main import app
from backend.database import data_dir


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(('127.0.0.1', 0))
        return listener.getsockname()[1]


def check_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + '/api/status', timeout=.8) as response:
            return response.status == 200 and b'Amicus Theologi' in response.read(2048)
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def make_server(port: int):
    config = uvicorn.Config(app, host='127.0.0.1', port=port,
                            log_level='warning', access_log=False)
    return uvicorn.Server(config)


def self_test() -> int:
    """Fast real bundled-EXE test without tkinter or an active browser."""
    with tempfile.TemporaryDirectory(prefix='amicus-selftest-') as folder:
        old = os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR'] = folder
        try:
            port = free_port()
            server = make_server(port)
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            url = f'http://127.0.0.1:{port}'
            for _ in range(80):
                if check_ready(url):
                    with urllib.request.urlopen(url+'/ANLEITUNG.html', timeout=3) as response:
                        text=response.read().decode('utf-8')
                        assert 'Volltextsuche' in text and 'Amicus Theologi' in text
                    with urllib.request.urlopen(url+'/ANLEITUNG.js', timeout=3) as response:
                        assert b'manual-search' in response.read()
                    print('SELF-TEST OK: server, database, manual')
                    return 0
                if not thread.is_alive():
                    break
                time.sleep(.15)
            print('SELF-TEST ERROR: server did not start',file=sys.stderr)
            return 1
        except Exception as exc:
            print(f'SELF-TEST ERROR: {exc}', file=sys.stderr)
            return 1
        finally:
            if 'server' in locals():
                server.should_exit=True
                if 'thread' in locals():thread.join(timeout=7)
            if old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
            else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=old


def start_desktop():
    """Show a control window, then start a local server and open browser."""
    import tkinter as tk
    from tkinter import messagebox

    root=tk.Tk()
    root.title('Amicus Theologi')
    root.geometry('380x240')
    root.minsize(355,225)
    root.configure(bg='#172c3e')
    try:
        # The data file is included by PyInstaller, but installation is optional.
        icon=Path(__file__).resolve().parent/'assets'/'amicus.ico'
        if not icon.exists():icon=Path(__file__).resolve().parent.parent/'assets'/'amicus.ico'
        if icon.exists():root.iconbitmap(str(icon))
    except Exception:pass
    if os.name != 'nt':
        # Linux desktop environments use PNG icons instead of Windows ICO.
        try:
            png = Path(__file__).resolve().parent.parent / 'assets' / 'amicus.png'
            if png.is_file():
                root._amicus_icon = tk.PhotoImage(file=str(png))
                root.iconphoto(True, root._amicus_icon)
        except Exception:
            pass
    tk.Label(root,text='Amicus Theologi',font=('Segoe UI',20,'bold'),
             bg='#172c3e',fg='#e7d3a5').pack(pady=(22,6))
    tk.Label(root,text='Wissenschaftliche Bibelarbeit · lokal auf diesem PC',
             font=('Segoe UI',10),bg='#172c3e',fg='#dbe3e9').pack()
    status=tk.StringVar(value='Anwendung wird gestartet …')
    tk.Label(root,textvariable=status,bg='#172c3e',fg='#b9cfdd',
             font=('Segoe UI',10)).pack(pady=(15,9))
    buttons=tk.Frame(root,bg='#172c3e');buttons.pack()
    open_button=tk.Button(buttons,text='Im Browser öffnen',state='disabled',
                          bg='#e8d1a1',fg='#1d3141',relief='flat',padx=13,pady=7)
    open_button.pack(side='left',padx=7)
    exit_button=tk.Button(buttons,text='Beenden',bg='#375268',fg='white',
                          relief='flat',padx=15,pady=7)
    exit_button.pack(side='left',padx=7)
    port=free_port();url=f'http://127.0.0.1:{port}'
    server=make_server(port)
    worker=threading.Thread(target=server.run,daemon=True,name='amicus-http-server')
    worker.start()
    closed=False
    def shutdown():
        nonlocal closed
        if closed:return
        closed=True
        server.should_exit=True
        root.destroy()
    root.protocol('WM_DELETE_WINDOW',shutdown)
    exit_button.configure(command=shutdown)
    open_button.configure(command=lambda:webbrowser.open(url,new=2))
    started=time.monotonic()
    def poll():
        if closed:return
        if check_ready(url):
            status.set('Bereit · läuft nur auf diesem Computer')
            open_button.configure(state='normal')
            webbrowser.open(url,new=2)
        elif not worker.is_alive() or time.monotonic()-started>40:
            status.set('Start fehlgeschlagen. Bitte erneut versuchen.')
            messagebox.showerror('Amicus Theologi',
                'Der lokale Dienst konnte nicht gestartet werden.\n'
                'Prüfe ggf. die Hinweise in der Bedienungsanleitung.')
            open_button.configure(state='disabled')
        else:root.after(280,poll)
    root.after(300,poll)
    root.mainloop()
    server.should_exit=True
    worker.join(timeout=6)


def desktop_shortcut():
    """Provide an optional GNOME desktop shortcut without root privileges."""
    from tkinter import Tk, messagebox
    import subprocess
    root=Tk()
    root.withdraw()
    try:
        if os.name == 'nt':
            messagebox.showinfo('Amicus Theologi', 'Diese Funktion ist für Ubuntu vorgesehen.', parent=root)
            return 0
        try:
            desktop=subprocess.run(['xdg-user-dir', 'DESKTOP'], capture_output=True,
                                   text=True, timeout=3, check=False).stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            desktop=''
        target_dir=Path(desktop).expanduser() if desktop else None
        if not target_dir or not target_dir.is_dir():
            target_dir=next((p for p in [Path.home()/'Schreibtisch', Path.home()/'Desktop'] if p.is_dir()), None)
        if target_dir is None:
            messagebox.showwarning('Amicus Theologi',
                'Es wurde kein Desktop-Ordner gefunden.\n'
                'Du kannst Amicus Theologi jederzeit über das Anwendungsmenü starten.', parent=root)
            return 1
        dest=target_dir/'amicus-theologi.desktop'
        if not messagebox.askyesno('Amicus Theologi',
            f'Desktopverknüpfung erstellen?\n\n{dest}', parent=root):
            return 0
        entry=('''[Desktop Entry]\nType=Application\nName=Amicus Theologi\n'''
               '''Comment=Wissenschaftliche Bibelarbeit und Exegese\n'''
               '''Exec=/opt/amicus-theologi/AmicusTheologi\n'''
               '''Icon=amicus-theologi\nTerminal=false\nCategories=Education;Science;\n''')
        if not Path('/opt/amicus-theologi/AmicusTheologi').exists():
            messagebox.showerror('Amicus Theologi',
                'Die installierte Anwendung wurde nicht gefunden.', parent=root)
            return 1
        dest.write_text(entry, encoding='utf-8')
        dest.chmod(0o755)
        try:
            subprocess.run(['gio','set',str(dest),'metadata::trusted','true'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=3, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        messagebox.showinfo('Amicus Theologi',
            'Die Desktopverknüpfung wurde erstellt.\n'
            'Je nach Ubuntu-Version muss sie beim ersten Start noch als vertrauenswürdig markiert werden.',
            parent=root)
        return 0
    finally:
        root.destroy()


def gui_self_test():
    """Checks that the bundled GUI and theme icon can be initialized."""
    import tkinter as tk
    root=tk.Tk()
    root.title('Amicus Theologi – GUI Test')
    png=Path(__file__).resolve().parent.parent/'assets'/'amicus.png'
    if os.name != 'nt' and png.is_file():
        root._amicus_icon=tk.PhotoImage(file=str(png))
        root.iconphoto(True, root._amicus_icon)
    root.update()
    root.destroy()
    print('GUI SELF-TEST OK')
    return 0


def main():
    if '--self-test' in sys.argv:
        return self_test()
    if '--gui-self-test' in sys.argv:
        return gui_self_test()
    if '--create-desktop-shortcut' in sys.argv:
        return desktop_shortcut()
    try:
        start_desktop()
        return 0
    except Exception:
        # Installed exe is windowed; errors should be accessible after a crash.
        try:
            out=data_dir()/'logs'
            out.mkdir(parents=True,exist_ok=True)
            logging.basicConfig(filename=out/'desktop-launcher.log',level=logging.ERROR)
            logging.exception('Launcher failed')
        except Exception:pass
        raise


if __name__=='__main__':
    sys.exit(main())
