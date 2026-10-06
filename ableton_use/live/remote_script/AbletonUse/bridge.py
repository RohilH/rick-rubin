# Control surface + socket server. Live API calls happen only on Live's main
# thread (update_display), never on the socket threads.
import json
import socket
import threading

try:  # Python 3
    import queue
except ImportError:  # pragma: no cover
    import Queue as queue  # noqa: N813

import Live  # provided by Ableton Live
from _Framework.ControlSurface import ControlSurface

from . import handlers as _handlers

HOST = "127.0.0.1"
PORT = 9889
MAX_PER_TICK = 64


class AbletonUse(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._inbox = queue.Queue()
        self._running = True
        self._handlers = None
        self._load_handlers()
        self._sock = None
        self._thread = threading.Thread(target=self._serve, name="ableton-use-bridge")
        self._thread.daemon = True
        self._thread.start()
        self.show_message("ableton-use bridge %s listening on %s:%d" % (_handlers.BRIDGE_VERSION, HOST, PORT))

    def _load_handlers(self):
        """(Re)read handlers.py from disk, so `ableton-use install-bridge` + the 'reload'
        command picks up handler changes without restarting Live."""
        try:
            import importlib
            importlib.reload(_handlers)
        except Exception as e:  # noqa: BLE001
            self._log("ableton-use: reload failed: %s" % e)
            if self._handlers is not None:
                raise
        self._handlers = _handlers.Handlers(self.song, Live.Application.get_application, Live, self._log)
        return {"bridge": _handlers.BRIDGE_VERSION}

    def _log(self, text, show=False):
        self.log_message(text)
        if show:
            self.show_message(text)

    # ------------------------------------------------------------- networking
    def _serve(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((HOST, PORT))
            self._sock.listen(4)
            self._sock.settimeout(1.0)
        except Exception as e:  # noqa: BLE001
            self._log("ableton-use: cannot bind %s:%d (%s)" % (HOST, PORT, e))
            return
        while self._running:
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except Exception:  # noqa: BLE001
                break
            t = threading.Thread(target=self._client, args=(conn,))
            t.daemon = True
            t.start()

    def _client(self, conn):
        buf = b""
        conn.settimeout(None)
        try:
            while self._running:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line.strip():
                        continue
                    try:
                        req = json.loads(line.decode("utf-8"))
                    except ValueError as e:
                        resp = {"ok": False, "error": "bad json: %s" % e}
                    else:
                        box = {"event": threading.Event(), "resp": None}
                        self._inbox.put((req, box))
                        if not box["event"].wait(float(req.get("timeout", 120))):
                            resp = {"ok": False, "error": "timeout waiting for Live main thread"}
                        else:
                            resp = box["resp"]
                    resp["id"] = req.get("id") if isinstance(req, dict) else None
                    conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
        except Exception as e:  # noqa: BLE001
            self._log("ableton-use client error: %s" % e)
        finally:
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------- main thread
    def update_display(self):
        ControlSurface.update_display(self)
        for _ in range(MAX_PER_TICK):
            try:
                req, box = self._inbox.get_nowait()
            except queue.Empty:
                break
            if isinstance(req, dict) and req.get("cmd") == "reload":
                try:
                    box["resp"] = {"ok": True, "result": self._load_handlers()}
                except Exception as e:  # noqa: BLE001
                    box["resp"] = {"ok": False, "error": "reload: %s" % e}
            else:
                box["resp"] = self._handlers.dispatch(req)
            box["event"].set()

    def disconnect(self):
        self._running = False
        try:
            if self._sock:
                self._sock.close()
        except Exception:  # noqa: BLE001
            pass
        ControlSurface.disconnect(self)
