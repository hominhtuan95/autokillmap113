"""Autoskill Hominhtuan95 - Windows 10/11, Python 3.10+.
Fixed license prompt on every launch. Uses standard library only.
"""
import ctypes
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = 'Autoskill Hominhtuan95'
# Dán public key do setup_license.py tạo vào đây. KHÔNG đưa private key lên GitHub.
PUBLIC_KEY_HEX = '9233b8f04e7f633e89dfc8a1835f14841e8eef4285daa16d96d146a560a92b4d'
MIN_DELAY_MS = 50
MAX_DELAY_MS = 180_000
DEFAULTS = [5000, 300] + [1000] * 10
LABELS = ['Tab', 'Space'] + [f'Skill {i}' for i in range(1, 11)]
VKS = [0x09, 0x20] + list(range(0x31, 0x3A)) + [0x30]
WM_KEYDOWN, WM_KEYUP = 0x0100, 0x0101
WM_SYSKEYDOWN, WM_SYSKEYUP = 0x0104, 0x0105
WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0201, 0x0202
VK_MENU, VK_D = 0x12, 0x44

if not hasattr(ctypes, 'windll'):
    raise SystemExit('This application only runs on Windows.')
user32 = ctypes.windll.user32
user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p), ctypes.c_void_p]
user32.EnumWindows.restype = ctypes.c_bool
user32.IsWindowVisible.argtypes = [ctypes.c_void_p]
user32.IsWindowVisible.restype = ctypes.c_bool
user32.IsWindow.argtypes = [ctypes.c_void_p]
user32.IsWindow.restype = ctypes.c_bool
user32.GetWindowTextLengthW.argtypes = [ctypes.c_void_p]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
user32.PostMessageW.restype = ctypes.c_bool
class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.ScreenToClient.argtypes = [ctypes.c_void_p, ctypes.POINTER(POINT)]


def machine_hwid():
    """Stable Windows MachineGuid hashed; avoids exposing raw machine identifier."""
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography') as key:
        guid, _ = winreg.QueryValueEx(key, 'MachineGuid')
    import hashlib
    return hashlib.sha256(('Autoskill-Hominhtuan95|' + guid).encode('utf-8')).hexdigest()[:32].upper()


def license_file():
    base = Path.home() / 'AppData' / 'Local' / 'AutoskillHominhtuan95'
    base.mkdir(parents=True, exist_ok=True)
    return base / 'license.txt'


def verify_license(token, hwid):
    try:
        payload_b64, signature_b64 = token.strip().split('.')
        payload = base64.urlsafe_b64decode(payload_b64 + '=' * (-len(payload_b64) % 4))
        signature = base64.urlsafe_b64decode(signature_b64 + '=' * (-len(signature_b64) % 4))
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUBLIC_KEY_HEX)).verify(signature, payload)
        data = json.loads(payload)
        return data.get('app') == APP_NAME and data.get('hwid') == hwid and data.get('version') == 1
    except Exception:
        return False


def license_prompt(root):
    accepted = {'value': False}
    hwid = machine_hwid()
    dlg = tk.Toplevel(root)
    dlg.title('Kích hoạt HWID - ' + APP_NAME)
    dlg.geometry('490x255')
    dlg.resizable(False, False)
    dlg.protocol('WM_DELETE_WINDOW', dlg.destroy)
    dlg.grab_set()
    ttk.Label(dlg, text=APP_NAME, font=('Segoe UI', 12, 'bold')).pack(pady=(12, 5))
    ttk.Label(dlg, text='Mã máy (HWID) - gửi mã này cho người cấp phép:').pack()
    frame = ttk.Frame(dlg)
    frame.pack(pady=5)
    hwid_var = tk.StringVar(master=dlg, value=hwid)
    ttk.Entry(frame, width=37, state='readonly', textvariable=hwid_var).pack(side='left')
    ttk.Button(frame, text='Sao chép', command=lambda: (dlg.clipboard_clear(), dlg.clipboard_append(hwid))).pack(side='left', padx=5)
    ttk.Label(dlg, text='Dán mã kích hoạt được cấp cho máy này:').pack(pady=(5, 0))
    key_var = tk.StringVar()
    entry = ttk.Entry(dlg, textvariable=key_var, width=65)
    entry.pack(pady=7)

    def activate(event=None):
        token = key_var.get().strip()
        if verify_license(token, hwid):
            license_file().write_text(token, encoding='utf-8')
            accepted['value'] = True
            dlg.destroy()
        else:
            messagebox.showerror('Mã không hợp lệ', 'Mã kích hoạt không đúng hoặc không thuộc máy này.', parent=dlg)

    ttk.Button(dlg, text='Kích hoạt', command=activate).pack()
    dlg.bind('<Return>', activate)
    dlg.after(50, entry.focus_set)
    root.wait_window(dlg)
    return accepted['value']


def licensed(root):
    hwid = machine_hwid()
    try:
        token = license_file().read_text(encoding='utf-8').strip()
        if verify_license(token, hwid):
            return True
    except OSError:
        pass
    return license_prompt(root)


class AutoSkill:
    """Each process has independent settings and a focus-only F1 shortcut."""
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME + ' - 10 Skill')
        root.geometry('430x950')
        root.minsize(430, 900)
        self.running = False
        self.closing = False
        self.stop_event = None
        self.hwnds = []
        self.hwnd = None
        self.status = tk.StringVar(value='Dừng | F1 khi chọn cửa sổ Auto')
        self.ms = [tk.StringVar(value=str(n)) for n in DEFAULTS]
        self.vars = [tk.BooleanVar(value=True) for _ in DEFAULTS]
        self.choice = tk.StringVar()
        self.train_enabled = tk.BooleanVar(value=False)
        self.train_x = tk.StringVar(value='168')
        self.train_y = tk.StringVar(value='80')
        self.return_minutes = tk.StringVar(value='0')
        self.route_enabled = tk.BooleanVar(value=True)
        self.route_minutes = tk.StringVar(value='5')
        self.map_points = {'x': None, 'y': None, 'go': None}
        self.calibration_pending = False

        ttk.Label(root, text=APP_NAME + ' | 10 SKILL', font=('Segoe UI', 11, 'bold')).pack(pady=(8, 5))
        line = ttk.Frame(root)
        line.pack(fill='x', padx=8)
        self.selector = ttk.Combobox(line, textvariable=self.choice, state='readonly', width=35)
        self.selector.pack(side='left', fill='x', expand=True)
        ttk.Button(line, text='↻', width=3, command=self.refresh).pack(side='left', padx=(3, 0))

        rows = ttk.Frame(root)
        rows.pack(fill='x', padx=15, pady=(10, 5))
        ttk.Label(rows, text='Bật / Phím', font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(rows, text='Chu kỳ (ms)', font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, sticky='e')
        rows.columnconfigure(0, weight=1)
        for i, label in enumerate(LABELS):
            key_label = f'{label} (0)' if label == 'Skill 10' else label
            ttk.Checkbutton(rows, text=key_label, variable=self.vars[i]).grid(row=i + 1, column=0, sticky='w', pady=2)
            ttk.Entry(rows, textvariable=self.ms[i], width=11, justify='right').grid(row=i + 1, column=1, sticky='e', pady=2)

        train = ttk.LabelFrame(root, text='Auto Train theo tọa độ (Alt + D)')
        train.pack(fill='x', padx=10, pady=(5, 0))
        ttk.Checkbutton(train, text='Bật Auto Train khi nhấn Chạy / F1', variable=self.train_enabled).pack(anchor='w', padx=7)
        coords = ttk.Frame(train)
        coords.pack(fill='x', padx=7, pady=3)
        ttk.Label(coords, text='X:').pack(side='left')
        ttk.Entry(coords, textvariable=self.train_x, width=7).pack(side='left', padx=(3, 10))
        ttk.Label(coords, text='Y:').pack(side='left')
        ttk.Entry(coords, textvariable=self.train_y, width=7).pack(side='left', padx=(3, 10))
        ttk.Label(coords, text='Quay về (phút):').pack(side='left')
        ttk.Entry(coords, textvariable=self.return_minutes, width=5).pack(side='left', padx=3)
        ttk.Label(train, text='0 = chỉ đến bãi train lúc bắt đầu; >0 = quay về theo chu kỳ', foreground='#555').pack(anchor='w', padx=7)
        ttk.Separator(train).pack(fill='x', padx=7, pady=5)
        ttk.Checkbutton(train, text='Đi tuần tự nhiều tọa độ (lặp vòng)', variable=self.route_enabled).pack(anchor='w', padx=7)
        ttk.Label(train, text='Mỗi dòng một tọa độ X,Y:').pack(anchor='w', padx=7)
        self.route_text = tk.Text(train, height=7, width=28, font=('Consolas', 9))
        self.route_text.pack(fill='x', padx=7, pady=2)
        self.route_text.insert('1.0', '265,122\n215,075\n121,086\n093,141\n130,182\n177,204\n245,146')
        route_row = ttk.Frame(train)
        route_row.pack(fill='x', padx=7, pady=2)
        ttk.Label(route_row, text='Chuyển điểm sau (phút):').pack(side='left')
        ttk.Entry(route_row, textvariable=self.route_minutes, width=6).pack(side='left', padx=5)
        ttk.Label(train, text='Điểm đầu ngay khi Chạy; sau mỗi 5 phút chuyển điểm tiếp theo.', foreground='#555', wraplength=390).pack(anchor='w', padx=7)
        cal = ttk.Frame(train)
        cal.pack(fill='x', padx=7, pady=4)
        for name, label in [('x', 'Lấy ô X'), ('y', 'Lấy ô Y'), ('go', 'Lấy Dò tìm')]:
            ttk.Button(cal, text=label, command=lambda k=name: self.calibrate(k)).pack(side='left', expand=True, fill='x', padx=2)
        ttk.Label(train, text='Mở bản đồ game trước, bấm Lấy rồi trỏ chuột vào vị trí cần lấy.',
                  foreground='#555', wraplength=355).pack(anchor='w', padx=7, pady=(0, 4))

        controls = ttk.Frame(root)
        controls.pack(fill='x', padx=10, pady=(6, 0))
        ttk.Button(controls, text='Chạy', command=self.start).pack(side='left', fill='x', expand=True, padx=(0, 3))
        ttk.Button(controls, text='Dừng', command=self.stop).pack(side='left', fill='x', expand=True)
        ttk.Label(root, textvariable=self.status, font=('Segoe UI', 9)).pack(pady=(9, 3))
        ttk.Label(root, text='50–180000 ms | F1 chỉ tác động cửa sổ Auto đang chọn',
                  foreground='#555', font=('Segoe UI', 8)).pack()
        # Tk processes this shortcut only while this AutoSkill window is focused.
        # No global hotkey: other AutoSkill processes remain unaffected.
        root.bind_all('<F1>', self.toggle_f1)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.refresh()

    def toggle_f1(self, event=None):
        if self.closing:
            return 'break'
        if self.running:
            self.stop()
        else:
            self.start()
        return 'break'

    def refresh(self):
        previous = self.hwnd
        found = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        @callback_type
        def callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                n = user32.GetWindowTextLengthW(hwnd)
                if n > 0:
                    buf = ctypes.create_unicode_buffer(n + 1)
                    user32.GetWindowTextW(hwnd, buf, n + 1)
                    title = buf.value
                    if 'chien quoc' in title.casefold() or 'chiến quốc' in title.casefold():
                        found.append((int(hwnd), title))
            return True

        user32.EnumWindows(callback, None)
        self.hwnds = found
        self.selector['values'] = [f'{hwnd} | {title[:32]}' for hwnd, title in found]
        if found:
            chosen = next((i for i, item in enumerate(found) if item[0] == previous), 0)
            self.selector.current(chosen)
        else:
            self.choice.set('Không thấy cửa sổ Chiến Quốc')

    def calibrate(self, which):
        idx = self.selector.current()
        if idx < 0 or idx >= len(self.hwnds):
            messagebox.showwarning('Chọn game', 'Hãy chọn cửa sổ Chiến Quốc trước.', parent=self.root)
            return
        if self.calibration_pending:
            return
        hwnd = self.hwnds[idx][0]
        self.calibration_pending = True
        self.status.set('Sau 4 giây sẽ lấy vị trí chuột: ' + which)
        # Dùng thời gian để người dùng chuyển sang game và trỏ vào ô cần lấy.
        def capture():
            self.calibration_pending = False
            if not user32.IsWindow(hwnd):
                self.status.set('Cửa sổ game đã đóng')
                return
            pt = POINT()
            if not user32.GetCursorPos(ctypes.byref(pt)) or not user32.ScreenToClient(hwnd, ctypes.byref(pt)):
                self.status.set('Không lấy được vị trí chuột')
                return
            self.map_points[which] = (pt.x, pt.y)
            self.status.set(f'Đã lưu {which}: ({pt.x}, {pt.y})')
        self.root.after(4000, capture)

    @staticmethod
    def post_key(hwnd, vk, stop_event, system=False):
        down, up = (WM_SYSKEYDOWN, WM_SYSKEYUP) if system else (WM_KEYDOWN, WM_KEYUP)
        user32.PostMessageW(hwnd, down, vk, (1 << 29) if system else 0)
        if stop_event.wait(0.055):
            user32.PostMessageW(hwnd, up, vk, 0)
            return False
        user32.PostMessageW(hwnd, up, vk, (1 << 29) if system else 0)
        return True

    @staticmethod
    def post_click(hwnd, point, stop_event):
        x, y = point
        lp = (y & 0xffff) << 16 | (x & 0xffff)
        user32.PostMessageW(hwnd, WM_LBUTTONDOWN, 1, lp)
        if stop_event.wait(0.075):
            user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lp)
            return False
        user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lp)
        return True

    def travel(self, hwnd, x, y, points, stop_event):
        # Thao tác theo đúng trình tự game: Alt+D, X, Y, Dò tìm, Alt+D.
        # Không đọc bộ nhớ game; game có thể không nhận PostMessage ở chế độ nền.
        def wait(t=0.25):
            return not stop_event.wait(t)
        user32.PostMessageW(hwnd, WM_SYSKEYDOWN, VK_MENU, 0)
        user32.PostMessageW(hwnd, WM_SYSKEYDOWN, VK_D, 1 << 29)
        user32.PostMessageW(hwnd, WM_SYSKEYUP, VK_D, 1 << 29)
        user32.PostMessageW(hwnd, WM_SYSKEYUP, VK_MENU, 0)
        if not wait(0.45): return False
        for key, value in [('x', str(x)), ('y', str(y))]:
            if not self.post_click(hwnd, points[key], stop_event) or not wait(0.1): return False
            # Ctrl+A rồi nhập số bằng mã phím 0-9 (không dùng clipboard).
            user32.PostMessageW(hwnd, WM_KEYDOWN, 0x11, 0)
            self.post_key(hwnd, 0x41, stop_event)
            user32.PostMessageW(hwnd, WM_KEYUP, 0x11, 0)
            for ch in value:
                if not self.post_key(hwnd, ord(ch), stop_event): return False
            if not wait(0.12): return False
        if not self.post_click(hwnd, points['go'], stop_event) or not wait(0.35): return False
        user32.PostMessageW(hwnd, WM_SYSKEYDOWN, VK_MENU, 0)
        user32.PostMessageW(hwnd, WM_SYSKEYDOWN, VK_D, 1 << 29)
        user32.PostMessageW(hwnd, WM_SYSKEYUP, VK_D, 1 << 29)
        user32.PostMessageW(hwnd, WM_SYSKEYUP, VK_MENU, 0)
        return not stop_event.is_set()

    def start(self):
        if self.running or self.closing:
            return
        idx = self.selector.current()
        if idx < 0 or idx >= len(self.hwnds):
            messagebox.showwarning('Chưa chọn game', 'Mở game và nhấn nút làm mới.', parent=self.root)
            return
        try:
            values = [int(v.get().strip()) for v in self.ms]
            if any(not MIN_DELAY_MS <= v <= MAX_DELAY_MS for v in values):
                raise ValueError
        except ValueError:
            messagebox.showerror('Sai thời gian', 'Nhập thời gian 50–180000 ms.', parent=self.root)
            return
        enabled = [v.get() for v in self.vars]
        if not any(enabled):
            messagebox.showwarning('Chưa chọn phím', 'Hãy bật ít nhất một phím.', parent=self.root)
            return
        train_config = None
        if self.train_enabled.get():
            try:
                if self.route_enabled.get():
                    route = []
                    for line in self.route_text.get('1.0', 'end').splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        parts = [v.strip() for v in line.split(',')]
                        if len(parts) != 2:
                            raise ValueError('Mỗi dòng phải có dạng X,Y')
                        x, y = map(int, parts)
                        if x < 0 or y < 0:
                            raise ValueError('Tọa độ không được âm')
                        route.append((x, y))
                    if not route:
                        raise ValueError('Danh sách tọa độ trống')
                    minutes = float(self.route_minutes.get().replace(',', '.'))
                    if not 0.1 <= minutes <= 1440:
                        raise ValueError('Chu kỳ phải từ 0.1 đến 1440 phút')
                    train_config = ('route', route, minutes * 60, dict(self.map_points))
                else:
                    x, y = int(self.train_x.get()), int(self.train_y.get())
                    minutes = float(self.return_minutes.get())
                    if x < 0 or y < 0 or minutes < 0:
                        raise ValueError('Tọa độ và thời gian phải không âm')
                    train_config = ('single', [(x, y)], minutes * 60, dict(self.map_points))
                if not all(self.map_points.values()):
                    messagebox.showwarning('Chưa hiệu chỉnh', 'Mở bản đồ rồi lấy vị trí ô X, ô Y và nút Dò tìm.', parent=self.root)
                    return
            except (ValueError, TypeError) as exc:
                messagebox.showerror('Cấu hình Auto Train', str(exc), parent=self.root)
                return
        hwnd = self.hwnds[idx][0]
        if not user32.IsWindow(hwnd):
            messagebox.showwarning('Cửa sổ không tồn tại', 'Làm mới danh sách game.', parent=self.root)
            return
        self.hwnd = hwnd
        self.stop_event = threading.Event()
        self.running = True
        self.status.set(f'Đang chạy | HWND {hwnd}')
        threading.Thread(target=self.worker,
                         args=(hwnd, [v / 1000 for v in values], enabled, self.stop_event, train_config),
                         daemon=True).start()

    def stop(self):
        if self.stop_event is not None:
            self.stop_event.set()
        self.running = False
        if not self.closing:
            self.status.set('Dừng | F1 khi chọn cửa sổ Auto')

    def worker(self, hwnd, delays, enabled, stop_event, train_config=None):
        if train_config:
            mode, route, interval, points = train_config
            route_index = 0
            x, y = route[route_index]
            if not self.travel(hwnd, x, y, points, stop_event):
                return
            next_return = time.monotonic() + interval if interval else None
        else:
            next_return = None
        due = [time.monotonic() + i * 0.04 for i in range(len(VKS))]
        while not stop_event.is_set():
            if not user32.IsWindow(hwnd):
                self.root.after(0, self.window_closed, stop_event)
                return
            now = time.monotonic()
            if next_return is not None and now >= next_return:
                if mode == 'route':
                    route_index = (route_index + 1) % len(route)
                x, y = route[route_index]
                if not self.travel(hwnd, x, y, points, stop_event):
                    return
                next_return = time.monotonic() + interval
                due = [time.monotonic() + i * 0.04 for i in range(len(VKS))]
                continue
            for i, vk in enumerate(VKS):
                if stop_event.is_set():
                    return
                if enabled[i] and now >= due[i]:
                    # Best effort: games using DirectInput/raw input may ignore PostMessage.
                    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 0)
                    if stop_event.wait(0.025):
                        user32.PostMessageW(hwnd, WM_KEYUP, vk, 0)
                        return
                    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0)
                    due[i] = time.monotonic() + delays[i]
            stop_event.wait(0.02)

    def window_closed(self, stop_event):
        if self.closing or self.stop_event is not stop_event:
            return
        self.stop()
        self.status.set('Cửa sổ game đã đóng')

    def close(self):
        self.closing = True
        self.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    root.withdraw()
    if not licensed(root):
        root.destroy()
        return
    root.deiconify()
    AutoSkill(root)
    root.mainloop()


if __name__ == '__main__':
    main()
