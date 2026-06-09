import io
import os
import re
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import pandas as pd
from scipy.integrate import trapezoid
from scipy import signal as sp_signal


BACKGROUND_PATH = r"D:/2-kurs Magistr 2025-2026-o'quv yillar/EEG dissertatsiya/EEG dastur software/Spektranaliz EEG+++/EEG spectrum background 700x700.svg"
BACKGROUND_FALLBACK_PATHS = [
    r"D:/2-kurs Magistr 2025-2026-o'quv yillar/EEG dissertatsiya/EEG dastur software/Spektranaliz EEG+++/EEG spectrum background 700x700.png",
    r"D:/2-kurs Magistr 2025-2026-o'quv yillar/EEG dissertatsiya/EEG dastur software/Spektranaliz EEG+++/EEG spectrum background 700x700.jpg",
    r"D:/2-kurs Magistr 2025-2026-o'quv yillar/EEG dissertatsiya/EEG dastur software/Spektranaliz EEG+++/EEG spectrum background 685x685.jpg",
]
WINDOW_W, WINDOW_H = 700, 700
LAYOUT_W, LAYOUT_H = 700, 700

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

DEFAULT_FS = 256.0
EEG_BANDS = {
    "Delta": (0.5, 4.0),
    "Theta": (4.0, 8.0),
    "Alpha": (8.0, 13.0),
    "Beta": (13.0, 30.0),
    "Gamma": (30.0, 40.0),
}
STATE_ORDER = [
    "Charchoq",
    "Uyqusizlik",
    "Normal",
    "Fokus",
    "Xayojonlanish",
    "Stress",
    "Meditativ holat",
]


class EEGSpektralTahlilDasturi:
    def __init__(self, root):
        self.root = root
        self.root.title("Spektranaliz EEG")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.minsize(600, 600)
        self.root.resizable(True, True)

        self.selected_file = None
        self.resize_job = None
        self.bg_path = BACKGROUND_PATH
        self.bg_is_svg = os.path.splitext(self.bg_path)[1].lower() == ".svg"
        self.bg_size = self.get_svg_size(self.bg_path) if self.bg_is_svg else None
        self.bg_original = None if self.bg_is_svg else Image.open(self.bg_path).convert("RGB")
        self.bg_fallback_original = self.load_background_fallback()
        self.bg_photo = None
        self.bg_error_shown = False

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_id = self.canvas.create_image(0, 0, anchor="nw")

        self.title_id = self.canvas.create_text(
            0, 0,
            text="Sportchining Elektroensefalografik(EEG) signallarini spektral tahlil qilish",
            fill="red",
            justify="center",
        )

        self.upload_label_id = self.canvas.create_text(
            0, 0,
            text="Elektroensefalografik(EEG) signal faylini yuklang:",
            fill="black",
            justify="center",
        )

        self.file_shadow = self.rounded_rect(0, 0, 1, 1, 1, fill="#b9dede", outline="")
        self.file_panel = self.rounded_rect(0, 0, 1, 1, 1, fill="#fbffff", outline="#f0a000", width=2)
        self.file_label_id = self.canvas.create_text(0, 0, text="Faylni tanlash:", fill="#777777")

        self.file_btn_shadow = self.rounded_rect(0, 0, 1, 1, 1, fill="#b8c2ce", outline="", tags="file_btn")
        self.file_btn = self.rounded_rect(0, 0, 1, 1, 1, fill="#f7f9fc", outline="#7d8795", width=1, tags="file_btn")
        self.file_btn_highlight = self.rounded_rect(0, 0, 1, 1, 1, fill="#ffffff", outline="", tags="file_btn")
        self.file_icon_photo = None
        self.file_icon_id = self.canvas.create_image(0, 0, anchor="center", tags="file_btn")
        self.file_btn_text = self.canvas.create_text(0, 0, text="Fayl tanlash", fill="#111111", tags="file_btn")

        self.main_shadow = self.rounded_rect(0, 0, 1, 1, 1, fill="#144e8d", outline="")
        self.main_btn = self.rounded_rect(0, 0, 1, 1, 1, fill="#2f80d8", outline="#1d5fa8", width=2, tags="result_btn")
        self.main_highlight = self.rounded_rect(0, 0, 1, 1, 1, fill="#4d9be6", outline="", tags="result_btn")
        self.main_text = self.canvas.create_text(0, 0, text="Natijani olish", fill="white", tags="result_btn")

        self.result_title_id = self.canvas.create_text(
            0, 0,
            text="Elektroensefalografik(EEG) spektral natijasi:",
            fill="black",
            justify="center",
        )

        self.result_shadow = self.rounded_rect(0, 0, 1, 1, 1, fill="#9fd6cf", outline="")
        self.result_panel = self.rounded_rect(0, 0, 1, 1, 1, fill="#eaffff", outline="#4f972d", width=2)
        self.placeholder_id = self.canvas.create_text(0, 0, text="Natijalar oynasi", fill="#837777", justify="center")

        self.result_box = tk.Text(root, bg="#eaffff", fg="#333333", relief="flat", bd=0, wrap="word")
        self.result_box_id = self.canvas.create_window(0, 0, window=self.result_box, state="hidden")
        self.copyright_id = self.canvas.create_text(
            0,
            0,
            text="©Murodov Elchin O‘ktamovich",
            fill="#1f4f5a",
            justify="center",
        )

        self.canvas.tag_bind("file_btn", "<Enter>", lambda event: self.hover_file(True))
        self.canvas.tag_bind("file_btn", "<Leave>", lambda event: self.hover_file(False))
        self.canvas.tag_bind("file_btn", "<Button-1>", lambda event: self.select_file())

        self.canvas.tag_bind("result_btn", "<Enter>", lambda event: self.hover_result(True))
        self.canvas.tag_bind("result_btn", "<Leave>", lambda event: self.hover_result(False))
        self.canvas.tag_bind("result_btn", "<Button-1>", lambda event: self.analyze_eeg())

        self.root.bind("<Configure>", self.on_resize)
        self.root.after(100, self.redraw)

    def rr_points(self, x1, y1, x2, y2, r):
        r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
        return [
            x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r,
            x1, y1 + r, x1, y1, x1 + r, y1,
        ]

    def rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        return self.canvas.create_polygon(self.rr_points(x1, y1, x2, y2, r), smooth=True, **kwargs)

    def set_rect(self, item, x1, y1, x2, y2, r):
        self.canvas.coords(item, *self.rr_points(x1, y1, x2, y2, r))

    def get_svg_size(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                svg_text = file.read(4096)
        except OSError:
            return WINDOW_W, WINDOW_H

        viewbox = re.search(r'viewBox=["\']\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s*["\']', svg_text)
        if viewbox:
            return float(viewbox.group(3)), float(viewbox.group(4))

        width = re.search(r'width=["\']([\d.]+)', svg_text)
        height = re.search(r'height=["\']([\d.]+)', svg_text)
        if width and height:
            return float(width.group(1)), float(height.group(1))

        return WINDOW_W, WINDOW_H

    def make_cover_background(self, width, height):
        if self.bg_is_svg:
            return self.render_svg_cover(width, height)
        return self.resize_cover(self.bg_original, width, height)

    def render_svg_cover(self, width, height):
        bg_w, bg_h = self.bg_size
        ratio = max(width / bg_w, height / bg_h)
        render_w = max(1, int(bg_w * ratio))
        render_h = max(1, int(bg_h * ratio))

        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(
                url=self.bg_path,
                output_width=render_w,
                output_height=render_h,
            )
            rendered = Image.open(io.BytesIO(png_bytes)).convert("RGB")
            return self.crop_center(rendered, width, height)
        except ImportError:
            pass

        try:
            from reportlab.graphics import renderPM
            from svglib.svglib import svg2rlg

            drawing = svg2rlg(self.bg_path)
            png_bytes = renderPM.drawToString(drawing, fmt="PNG")
            rendered = Image.open(io.BytesIO(png_bytes)).convert("RGB")
            return self.resize_cover(rendered, width, height)
        except ImportError:
            pass

        if self.bg_fallback_original is not None:
            return self.resize_cover(self.bg_fallback_original, width, height)

        raise ImportError(
            "SVG fonni ishlatish uchun SVG renderer kerak.\n"
            "O'rnatish: pip install cairosvg\n"
            "Muqobil: pip install svglib reportlab\n"
            "Yoki shu papkaga 'EEG spectrum background 700x700.png' faylini joylashtiring."
        )

    def load_background_fallback(self):
        for path in BACKGROUND_FALLBACK_PATHS:
            if os.path.exists(path):
                try:
                    return Image.open(path).convert("RGB")
                except Exception:
                    continue
        return None

    def resize_cover(self, image, width, height):
        img_w, img_h = image.size
        ratio = max(width / img_w, height / img_h)
        resized = image.resize((max(1, int(img_w * ratio)), max(1, int(img_h * ratio))), RESAMPLE)
        return self.crop_center(resized, width, height)

    def crop_center(self, image, width, height):
        left = max(0, (image.width - width) // 2)
        top = max(0, (image.height - height) // 2)
        return image.crop((left, top, left + width, top + height))

    def make_folder_icon(self, size):
        size = max(18, int(size))
        stroke = max(2, size // 12)
        pad = max(3, size // 8)

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        shadow_offset = max(1, size // 16)
        body_top = int(size * 0.38)
        body_bottom = size - pad
        left = pad
        right = size - pad

        tab_left = left
        tab_top = int(size * 0.23)
        tab_right = int(size * 0.48)
        tab_bottom = body_top + stroke

        shadow = [
            (left + shadow_offset, body_top + shadow_offset),
            (right + shadow_offset, body_top + shadow_offset),
            (int(size * 0.84) + shadow_offset, body_bottom + shadow_offset),
            (left + shadow_offset, body_bottom + shadow_offset),
        ]
        draw.polygon(shadow, fill=(182, 192, 205, 150))

        tab = [
            (tab_left, tab_bottom),
            (tab_left, tab_top),
            (tab_right, tab_top),
            (int(size * 0.58), body_top),
            (right, body_top),
            (right, tab_bottom),
        ]
        draw.polygon(tab, fill="#f7fbff", outline="#111111")
        draw.line(tab + [tab[0]], fill="#111111", width=stroke, joint="curve")

        body = [
            (left, body_top),
            (right, body_top),
            (int(size * 0.84), body_bottom),
            (left, body_bottom),
        ]
        draw.polygon(body, fill="#ffffff", outline="#111111")
        draw.line(body + [body[0]], fill="#111111", width=stroke, joint="curve")

        lip_y = int(size * 0.56)
        draw.line(
            [(left + stroke * 2, lip_y), (right - stroke * 2, lip_y)],
            fill="#111111",
            width=max(1, stroke - 1),
        )

        return img

    def update_file_icon(self, x1, y1, x2, y2):
        btn_w = x2 - x1
        btn_h = y2 - y1
        icon_size = min(btn_h * 0.48, btn_w * 0.16)
        icon_x = x1 + btn_w * 0.17
        icon_y = y1 + btn_h * 0.52
        self.file_icon_photo = ImageTk.PhotoImage(self.make_folder_icon(icon_size))
        self.canvas.itemconfig(self.file_icon_id, image=self.file_icon_photo)
        self.canvas.coords(self.file_icon_id, icon_x, icon_y)
        return icon_x + icon_size / 2

    def fit_file_button_text(self, text, max_width, preferred_size):
        size = preferred_size
        while size > 7:
            check_font = tkfont.Font(family="Arial", size=size, weight="bold")
            if check_font.measure(text) <= max_width:
                return size
            size -= 1
        return 7

    def on_resize(self, event):
        if event.widget == self.root:
            if self.resize_job:
                self.root.after_cancel(self.resize_job)
            self.resize_job = self.root.after(30, self.redraw)

    def redraw(self):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w < 100 or h < 100:
            return

        sx, sy = w / LAYOUT_W, h / LAYOUT_H
        s = min(sx, sy)
        font = lambda size: max(9, int(size * s))
        x = lambda value: value * sx
        y = lambda value: value * sy

        try:
            bg = self.make_cover_background(w, h)
        except Exception as error:
            bg = Image.new("RGB", (w, h), "#dffafa")
            if not self.bg_error_shown:
                self.bg_error_shown = True
                messagebox.showerror("Fon rasmi xatosi", str(error))
        self.bg_photo = ImageTk.PhotoImage(bg)
        self.canvas.itemconfig(self.bg_id, image=self.bg_photo)
        self.canvas.tag_lower(self.bg_id)

        self.canvas.itemconfig(self.title_id, font=("Times New Roman", font(24), "bold italic"), width=int(w * 0.96))
        self.canvas.coords(self.title_id, x(342), y(63))

        self.canvas.itemconfig(self.upload_label_id, font=("Times New Roman", font(18), "bold"), width=int(w * 0.40))
        self.canvas.coords(self.upload_label_id, x(183), y(186))

        self.set_rect(self.file_shadow, x(332), y(157), x(642), y(215), font(10))
        self.set_rect(self.file_panel, x(328), y(153), x(638), y(211), font(10))
        self.canvas.itemconfig(self.file_label_id, font=("Times New Roman", font(15), "italic"))
        self.canvas.coords(self.file_label_id, x(420), y(182))

        bx1, by1, bx2, by2 = x(492), y(159), x(630), y(204)
        self.set_rect(self.file_btn_shadow, bx1 + x(2), by1 + y(3), bx2 + x(2), by2 + y(3), font(9))
        self.set_rect(self.file_btn, bx1, by1, bx2, by2, font(9))
        self.set_rect(self.file_btn_highlight, bx1 + x(4), by1 + y(4), bx2 - x(4), by1 + y(20), font(7))

        btn_w = bx2 - bx1
        icon_right = self.update_file_icon(bx1, by1, bx2, by2)
        text_left = max(icon_right + btn_w * 0.08, bx1 + btn_w * 0.34)
        text_right = bx2 - btn_w * 0.08
        text_width = max(20, text_right - text_left)
        file_text_size = self.fit_file_button_text("Fayl tanlash", text_width, font(10))

        self.canvas.itemconfig(self.file_btn_text, font=("Arial", file_text_size, "bold"))
        self.canvas.coords(self.file_btn_text, (text_left + text_right) / 2, by1 + (by2 - by1) * 0.52)

        self.set_rect(self.main_shadow, x(217), y(246), x(473), y(304), font(12))
        self.set_rect(self.main_btn, x(214), y(242), x(470), y(300), font(12))
        self.set_rect(self.main_highlight, x(219), y(247), x(465), y(270), font(9))
        self.canvas.itemconfig(self.main_text, font=("Times New Roman", font(22), "bold"))
        self.canvas.coords(self.main_text, x(342), y(270))

        self.canvas.itemconfig(self.result_title_id, font=("Times New Roman", font(20), "bold"), width=int(w * 0.9))
        self.canvas.coords(self.result_title_id, x(342), y(344))

        self.set_rect(self.result_shadow, x(82), y(380), x(611), y(644), font(12))
        self.set_rect(self.result_panel, x(78), y(376), x(607), y(640), font(12))
        self.canvas.itemconfig(self.placeholder_id, font=("Times New Roman", font(30), "italic"))
        self.canvas.coords(self.placeholder_id, x(342), y(508))

        self.result_box.config(font=("Times New Roman", font(14), "italic"))
        self.canvas.coords(self.result_box_id, x(342), y(508))
        self.canvas.itemconfig(self.result_box_id, width=int(x(485)), height=int(y(214)))

        self.canvas.itemconfig(self.copyright_id, font=("Times New Roman", font(11), "bold"))
        self.canvas.coords(self.copyright_id, x(342), y(664))

    def hover_file(self, active):
        self.canvas.config(cursor="hand2" if active else "")
        self.canvas.itemconfig(self.file_btn, fill="#edf4ff" if active else "#f7f9fc")
        self.canvas.itemconfig(self.file_btn_highlight, fill="#ffffff" if active else "#ffffff")
        self.canvas.itemconfig(self.file_btn_shadow, fill="#9fb3cc" if active else "#b8c2ce")

    def hover_result(self, active):
        self.canvas.config(cursor="hand2" if active else "")
        self.canvas.itemconfig(self.main_btn, fill="#2272c7" if active else "#2f80d8")
        self.canvas.itemconfig(self.main_highlight, fill="#5aa7ef" if active else "#4d9be6")

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="EEG signal faylini tanlang",
            filetypes=[
                ("EEG files", "*.edf *.EDF *.bdf *.BDF *.csv *.CSV"),
                ("EDF/EDF+ files", "*.edf *.EDF"),
                ("BDF/BDF+ files", "*.bdf *.BDF"),
                ("CSV files", "*.csv *.CSV"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.selected_file = file_path
            self.canvas.itemconfig(self.file_label_id, text=os.path.basename(file_path))

    def analyze_eeg(self):
        if not self.selected_file:
            messagebox.showwarning("Ogohlantirish", "Avval EEG signal faylini tanlang!")
            return

        try:
            raw_data, fs, source_info = self.load_signal(self.selected_file)
            if raw_data.shape[1] < 10:
                raise ValueError("Signal juda qisqa.")

            cleaned = self.preprocess_eeg(raw_data, fs)
            features = self.extract_spectral_features(cleaned, fs)
            scores, detected_state = self.evaluate_state(features)
            result_text = self.format_results(source_info, features, scores, detected_state)

            self.canvas.itemconfig(self.placeholder_id, state="hidden")
            self.canvas.itemconfig(self.result_box_id, state="normal")
            self.result_box.delete("1.0", "end")
            self.result_box.insert("end", result_text)

        except Exception as error:
            messagebox.showerror("Xatolik", f"Faylni tahlil qilib bo'lmadi:\n{error}")

    def load_signal(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
            return self.load_csv_signal(file_path)
        if ext in (".edf", ".bdf"):
            return self.load_edf_bdf_signal(file_path, ext)
        raise ValueError("Faqat EDF/EDF+/BDF/BDF+/CSV formatlari qo'llab-quvvatlanadi.")

    def load_csv_signal(self, file_path):
        try:
            df = pd.read_csv(file_path, sep=None, engine="python")
        except Exception:
            df = pd.read_csv(file_path, sep=None, engine="python", header=None)

        numeric_df = df.apply(pd.to_numeric, errors="coerce")
        numeric_df = numeric_df.dropna(axis=0, how="all").dropna(axis=1, how="all")
        if numeric_df.empty:
            raise ValueError("CSV faylda sonli EEG ma'lumotlari topilmadi.")

        fs = DEFAULT_FS
        channel_df = numeric_df

        if numeric_df.shape[1] >= 2:
            first_col = numeric_df.iloc[:, 0].dropna().to_numpy(dtype=float)
            if first_col.size > 3:
                diffs = np.diff(first_col)
                if np.all(diffs > 0):
                    detected_fs = 1.0 / np.median(diffs)
                    if 20 <= detected_fs <= 5000:
                        fs = float(detected_fs)
                        channel_df = numeric_df.iloc[:, 1:]

        channel_df = channel_df.dropna(axis=1, how="all")
        if channel_df.empty:
            raise ValueError("CSV faylda EEG kanallari topilmadi.")

        data = channel_df.to_numpy(dtype=float).T
        data = data[~np.all(~np.isfinite(data), axis=1)]
        if data.size == 0:
            raise ValueError("CSV faylda yaroqli EEG signali topilmadi.")

        source_info = {
            "file": os.path.basename(file_path),
            "format": "CSV",
            "channels": data.shape[0],
            "samples": data.shape[1],
            "fs": fs,
        }
        return data, fs, source_info

    def load_edf_bdf_signal(self, file_path, ext):
        try:
            return self.load_with_mne(file_path, ext)
        except ImportError:
            return self.load_with_pyedflib(file_path, ext)
        except Exception as mne_error:
            try:
                return self.load_with_pyedflib(file_path, ext)
            except Exception as pyedflib_error:
                raise ValueError(
                    "EDF/BDF faylni o'qish uchun 'mne' yoki 'pyedflib' kutubxonasi kerak.\n"
                    f"MNE xatosi: {mne_error}\nPyEDFlib xatosi: {pyedflib_error}"
                )

    def load_with_mne(self, file_path, ext):
        try:
            import mne
        except ImportError as error:
            raise ImportError from error

        if ext == ".bdf":
            raw = mne.io.read_raw_bdf(file_path, preload=True, verbose=False)
            file_format = "BDF/BDF+"
        else:
            raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
            file_format = "EDF/EDF+"

        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude="bads")
        if len(eeg_picks) > 0:
            raw.pick(eeg_picks)

        data = raw.get_data()
        if data.size == 0:
            raise ValueError("EDF/BDF faylda EEG kanallari topilmadi.")

        fs = float(raw.info["sfreq"])
        source_info = {
            "file": os.path.basename(file_path),
            "format": file_format,
            "channels": data.shape[0],
            "samples": data.shape[1],
            "fs": fs,
        }
        return data, fs, source_info

    def load_with_pyedflib(self, file_path, ext):
        try:
            import pyedflib
        except ImportError as error:
            raise ImportError from error

        reader = pyedflib.EdfReader(file_path)
        try:
            channel_count = reader.signals_in_file
            if channel_count == 0:
                raise ValueError("EDF/BDF faylda signal kanallari topilmadi.")

            labels = reader.getSignalLabels()
            fs_values = np.array([reader.getSampleFrequency(i) for i in range(channel_count)], dtype=float)
            eeg_indexes = [
                i for i, label in enumerate(labels)
                if any(key in label.upper() for key in ("EEG", "FP", "F", "C", "P", "O", "T"))
            ]
            if not eeg_indexes:
                eeg_indexes = list(range(channel_count))

            target_fs = float(np.median(fs_values[eeg_indexes]))
            durations = [reader.getNSamples()[i] / fs_values[i] for i in eeg_indexes]
            duration = min(durations)
            target_samples = max(1, int(duration * target_fs))

            channels = []
            for index in eeg_indexes:
                current_fs = fs_values[index]
                current_samples = int(duration * current_fs)
                channel = reader.readSignal(index)[:current_samples].astype(float)
                if current_samples != target_samples:
                    channel = sp_signal.resample(channel, target_samples)
                channels.append(channel)

            data = np.vstack(channels)
            source_info = {
                "file": os.path.basename(file_path),
                "format": "BDF/BDF+" if ext == ".bdf" else "EDF/EDF+",
                "channels": data.shape[0],
                "samples": data.shape[1],
                "fs": target_fs,
            }
            return data, target_fs, source_info
        finally:
            reader.close()

    def preprocess_eeg(self, data, fs):
        data = np.asarray(data, dtype=float)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        if fs <= 5:
            raise ValueError("Diskretlash chastotasi noto'g'ri aniqlangan.")

        cleaned = []
        for channel in data:
            channel = self.fill_missing_values(channel)
            median = np.median(channel)
            mad = np.median(np.abs(channel - median))
            robust_std = 1.4826 * mad if mad > 0 else np.std(channel)
            if robust_std > 0:
                channel = np.clip(channel, median - 6 * robust_std, median + 6 * robust_std)
            cleaned.append(channel)

        data = np.vstack(cleaned)
        data = sp_signal.detrend(data, axis=1, type="linear")

        if data.shape[1] > int(fs * 0.5):
            for notch_freq in (50.0, 60.0):
                if notch_freq < fs / 2 - 1:
                    try:
                        b, a = sp_signal.iirnotch(notch_freq, Q=30, fs=fs)
                        data = sp_signal.filtfilt(b, a, data, axis=1)
                    except ValueError:
                        pass

            high_cut = min(40.0, fs / 2 - 1.0)
            if high_cut > 0.5:
                try:
                    sos = sp_signal.butter(4, [0.5, high_cut], btype="bandpass", fs=fs, output="sos")
                    data = sp_signal.sosfiltfilt(sos, data, axis=1)
                except ValueError:
                    pass

        mean = np.mean(data, axis=1, keepdims=True)
        std = np.std(data, axis=1, keepdims=True)
        return (data - mean) / (std + 1e-12)

    def fill_missing_values(self, values):
        values = np.asarray(values, dtype=float)
        finite = np.isfinite(values)
        if finite.sum() < 10:
            raise ValueError("Signal kanalida yaroqli nuqtalar juda kam.")
        if finite.all():
            return values
        x = np.arange(values.size)
        return np.interp(x, x[finite], values[finite])

    def extract_spectral_features(self, data, fs):
        n_samples = data.shape[1]
        window_samples = int(min(n_samples, max(fs * 2, fs * 4)))
        window_samples = max(16, window_samples)
        if window_samples > n_samples:
            window_samples = n_samples
        step_samples = max(1, window_samples // 2)

        band_records = []
        entropy_records = []
        dominant_records = []
        edge_records = []
        fft_dominant_records = []

        starts = list(range(0, n_samples - window_samples + 1, step_samples))
        if not starts:
            starts = [0]

        for channel in data:
            for start in starts:
                segment = channel[start:start + window_samples]
                if segment.size < 16 or np.std(segment) < 1e-12:
                    continue

                nperseg = min(segment.size, max(64, int(fs * 2)))
                frequencies, psd = sp_signal.welch(segment, fs=fs, nperseg=nperseg)
                band_power = {}
                for band_name, (low, high) in EEG_BANDS.items():
                    band_power[band_name] = self.band_power(frequencies, psd, low, high)
                band_records.append(band_power)

                valid = (frequencies >= 0.5) & (frequencies <= min(40.0, fs / 2 - 1.0))
                if np.any(valid):
                    f_valid = frequencies[valid]
                    p_valid = psd[valid] + 1e-15
                    p_norm = p_valid / np.sum(p_valid)
                    entropy = -np.sum(p_norm * np.log2(p_norm)) / np.log2(p_norm.size)
                    entropy_records.append(float(entropy))

                    dominant_records.append(float(f_valid[np.argmax(p_valid)]))
                    cumulative = np.cumsum(p_valid)
                    edge_index = np.searchsorted(cumulative, 0.95 * cumulative[-1])
                    edge_records.append(float(f_valid[min(edge_index, f_valid.size - 1)]))

                fft_freq = np.fft.rfftfreq(segment.size, d=1.0 / fs)
                fft_amp = np.abs(np.fft.rfft(segment))
                fft_mask = (fft_freq >= 0.5) & (fft_freq <= min(40.0, fs / 2 - 1.0))
                if np.any(fft_mask):
                    fft_dominant_records.append(float(fft_freq[fft_mask][np.argmax(fft_amp[fft_mask])]))

        if not band_records:
            raise ValueError("Spektral xususiyatlarni hisoblash uchun signal yetarli emas.")

        powers = {
            band: float(np.mean([record[band] for record in band_records]))
            for band in EEG_BANDS
        }
        total_power = sum(powers.values()) + 1e-12
        relative = {band: powers[band] / total_power for band in EEG_BANDS}

        features = {
            "band_power": powers,
            "relative_power": relative,
            "alpha_beta_ratio": powers["Alpha"] / (powers["Beta"] + 1e-12),
            "theta_beta_ratio": powers["Theta"] / (powers["Beta"] + 1e-12),
            "beta_alpha_ratio": powers["Beta"] / (powers["Alpha"] + 1e-12),
            "engagement_index": powers["Beta"] / (powers["Alpha"] + powers["Theta"] + 1e-12),
            "spectral_entropy": float(np.mean(entropy_records)) if entropy_records else 0.0,
            "dominant_frequency": float(np.mean(dominant_records)) if dominant_records else 0.0,
            "fft_dominant_frequency": float(np.mean(fft_dominant_records)) if fft_dominant_records else 0.0,
            "spectral_edge_95": float(np.mean(edge_records)) if edge_records else 0.0,
            "segments": len(band_records),
        }
        return features

    def band_power(self, frequencies, psd, low, high):
        high = min(high, frequencies[-1])
        indexes = (frequencies >= low) & (frequencies <= high)
        if np.count_nonzero(indexes) < 2:
            return 0.0
        return float(trapezoid(psd[indexes], frequencies[indexes]))

    def evaluate_state(self, features):
        rel = features["relative_power"]
        alpha = rel["Alpha"]
        beta = rel["Beta"]
        theta = rel["Theta"]
        delta = rel["Delta"]
        gamma = rel["Gamma"]
        low_freq = delta + theta
        fast_freq = beta + gamma
        entropy = features["spectral_entropy"]
        dominant = features["dominant_frequency"]
        edge = features["spectral_edge_95"]
        alpha_beta = features["alpha_beta_ratio"]
        theta_beta = features["theta_beta_ratio"]
        beta_alpha = features["beta_alpha_ratio"]
        engagement = features["engagement_index"]

        def scale(value, low, high):
            if high == low:
                return 0.0
            return float(np.clip((value - low) / (high - low), 0, 1))

        def bell(value, center, width):
            return float(np.clip(1 - abs(value - center) / width, 0, 1))

        scores = {
            "Charchoq": 100 * (
                0.35 * scale(low_freq, 0.42, 0.72)
                + 0.30 * scale(theta_beta, 1.8, 5.0)
                + 0.20 * scale(delta, 0.12, 0.35)
                + 0.15 * (1 - scale(fast_freq, 0.20, 0.48))
            ),
            "Uyqusizlik": 100 * (
                0.35 * scale(beta, 0.20, 0.42)
                + 0.25 * scale(gamma, 0.06, 0.20)
                + 0.20 * (1 - scale(alpha, 0.18, 0.42))
                + 0.20 * scale(entropy, 0.62, 0.92)
            ),
            "Normal": 100 * (
                0.25 * bell(alpha, 0.32, 0.24)
                + 0.20 * bell(beta, 0.20, 0.16)
                + 0.20 * bell(theta, 0.18, 0.16)
                + 0.20 * bell(dominant, 10.0, 5.0)
                + 0.15 * bell(entropy, 0.70, 0.30)
            ),
            "Fokus": 100 * (
                0.35 * scale(engagement, 0.35, 0.95)
                + 0.25 * scale(beta, 0.18, 0.35)
                + 0.20 * (1 - scale(theta, 0.14, 0.34))
                + 0.20 * scale(edge, 18.0, 32.0)
            ),
            "Xayojonlanish": 100 * (
                0.35 * scale(fast_freq, 0.28, 0.55)
                + 0.25 * scale(beta_alpha, 0.8, 2.4)
                + 0.20 * scale(gamma, 0.05, 0.18)
                + 0.20 * scale(entropy, 0.60, 0.92)
            ),
            "Stress": 100 * (
                0.40 * scale(beta_alpha, 0.9, 2.8)
                + 0.25 * scale(edge, 20.0, 35.0)
                + 0.20 * scale(gamma, 0.06, 0.22)
                + 0.15 * (1 - scale(alpha, 0.18, 0.40))
            ),
            "Meditativ holat": 100 * (
                0.35 * scale(alpha + theta, 0.42, 0.72)
                + 0.25 * scale(alpha_beta, 1.3, 4.0)
                + 0.20 * (1 - scale(beta, 0.16, 0.35))
                + 0.20 * bell(dominant, 9.0, 5.0)
            ),
        }

        scores = {name: round(float(np.clip(value, 0, 100)), 1) for name, value in scores.items()}
        detected_state = max(scores, key=scores.get)
        return scores, detected_state

    def format_results(self, source_info, features, scores, detected_state):
        powers = features["band_power"]
        relative = features["relative_power"]

        lines = [
            "EEG SPEKTRAL TAHLIL NATIJALARI",
            "",
            f"Fayl: {source_info['file']}",
            f"Format: {source_info['format']}",
            f"Kanallar soni: {source_info['channels']}",
            f"Sampling rate: {source_info['fs']:.2f} Hz",
            f"Segmentlar soni: {features['segments']}",
            "",
            f"Yakuniy baholangan holat: {detected_state}",
            "",
            "Holatlar bo'yicha indekslar (0-100):",
        ]

        for state in STATE_ORDER:
            marker = "  <-- eng yuqori" if state == detected_state else ""
            lines.append(f"{state}: {scores[state]:.1f}{marker}")

        lines.extend([
            "",
            "Chastota diapazonlari bo'yicha quvvat:",
        ])
        for band_name, (low, high) in EEG_BANDS.items():
            lines.append(
                f"{band_name} ({low:g}-{high:g} Hz): "
                f"{powers[band_name]:.6f} | nisbiy quvvat: {relative[band_name] * 100:.2f}%"
            )

        lines.extend([
            "",
            "Spektral xususiyatlar:",
            f"Alpha/Beta nisbati: {features['alpha_beta_ratio']:.3f}",
            f"Theta/Beta nisbati: {features['theta_beta_ratio']:.3f}",
            f"Beta/Alpha nisbati: {features['beta_alpha_ratio']:.3f}",
            f"Engagement indeksi: {features['engagement_index']:.3f}",
            f"Spektral entropiya: {features['spectral_entropy']:.3f}",
            f"Dominant chastota (PSD): {features['dominant_frequency']:.2f} Hz",
            f"Dominant chastota (FFT): {features['fft_dominant_frequency']:.2f} Hz",
            f"Spectral edge 95%: {features['spectral_edge_95']:.2f} Hz",
            "",
            "Eslatma: Natija spektral indekslarga asoslangan dasturiy baholashdir, klinik tashxis sifatida ishlatilmaydi.",
        ])
        return "\n".join(lines)

        numeric_data = df.select_dtypes(include=[np.number])
        if numeric_data.empty:
            raise ValueError("Faylda sonli EEG signal ma'lumotlari topilmadi.")

        return numeric_data.iloc[:, 0].dropna().to_numpy(dtype=float)


if __name__ == "__main__":
    root = tk.Tk()
    app = EEGSpektralTahlilDasturi(root)
    root.mainloop()
