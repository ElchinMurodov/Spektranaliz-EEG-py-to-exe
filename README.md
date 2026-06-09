# Spektranaliz EEG — .exe va o'rnatuvchi (setup) yasash bo'yicha qo'llanma

**Sportchining Elektroensefalografik (EEG) signallarini spektral tahlil qilish algoritmi va dasturiy vositasi**

Muallif: **Murodov Elchin O'ktamovich**

Bu qo'llanma `Spektranaliz EEG+++.py` dasturini logo, ikona va fon rasmlaridan
foydalangan holda Windows uchun `.exe` ko'rinishiga keltirish va o'rnatuvchi
(`setup.exe`) yasashni tushuntiradi.

---

## 1. Talablar (Windows kompyuterda)

- **Windows 10 / 11** (64-bit)
- **Python 3.10 yoki undan yuqori** — [python.org](https://www.python.org/downloads/)
  dan yuklab oling. O'rnatishda **"Add Python to PATH"** katakchasini belgilang.
- **(Ixtiyoriy) Inno Setup 6** — o'rnatuvchi (`setup.exe`) yasash uchun:
  [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)

> Eslatma: `.exe` faqat Windows'da yig'iladi. PyInstaller har bir operatsion
> tizim uchun alohida ishlatiladi (Windows'da yig'ilgan `.exe` Windows uchun).

---

## 2. Eng oson yo'l — bitta buyruq (avtomatik)

Loyiha papkasidagi **`build.bat`** faylini ikki marta bosing (yoki `cmd` da
ishga tushiring). U avtomatik ravishda quyidagilarni bajaradi:

1. Virtual muhit (`.venv`) yaratadi
2. Kerakli kutubxonalarni o'rnatadi (`requirements.txt`)
3. SVG ikonadan `.ico` fayl yasaydi (`make_ico.py`)
4. PyInstaller orqali `.exe` yig'adi (`spektranaliz_eeg.spec`)
5. Inno Setup o'rnatilgan bo'lsa, `setup.exe` ni ham yasaydi

**Natijalar:**
- Dastur (papkali): `dist\Spektranaliz EEG\Spektranaliz EEG.exe`
- O'rnatuvchi: `installer\Spektranaliz-EEG-Setup.exe`

---

## 3. Qo'lda yig'ish (qadamma-qadam)

```bat
:: 1) Virtual muhit
python -m venv .venv
.venv\Scripts\activate

:: 2) Kutubxonalar
pip install -r requirements.txt

:: 3) Ikonka (.ico) yasash
python make_ico.py

:: 4) .exe yig'ish
pyinstaller --noconfirm --clean spektranaliz_eeg.spec
```

Yig'ilgan dastur: `dist\Spektranaliz EEG\` papkasida. Ichidagi
`Spektranaliz EEG.exe` faylini ishga tushirib sinab ko'rishingiz mumkin.

### O'rnatuvchi (setup.exe) yasash

Inno Setup 6 o'rnatilgandan so'ng:

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

yoki `installer.iss` faylini Inno Setup Compiler'da ochib **Compile** bosing.
Natija: `installer\Spektranaliz-EEG-Setup.exe`.

Bu `setup.exe` foydalanuvchi kompyuteriga dasturni o'rnatadi, Start Menu va
(tanlasa) Ish stolida ikonkali yorliq yaratadi va "Dasturlarni o'chirish"
ro'yxatiga qo'shadi.

---

## 4. Loyiha fayllari

| Fayl | Vazifasi |
|------|----------|
| `Spektranaliz EEG+++.py` | Asosiy dastur (resurs yo'llari `resource_path()` orqali) |
| `requirements.txt` | Zarur Python kutubxonalari |
| `make_ico.py` | SVG ikonadan ko'p o'lchamli `.ico` yasaydi |
| `spektranaliz_eeg.spec` | PyInstaller sozlamasi (resurslarni `.exe` ga bundle qiladi) |
| `installer.iss` | Inno Setup o'rnatuvchi skripti |
| `build.bat` | Hammasini avtomatik bajaruvchi skript |
| `spektranaliz-eeg-icon.svg` | Dastur ikonkasi (manba) |
| `EEG spectrum background 700x700.svg` | Fon rasmi (asosiy) |
| `EEG-spectrum-background-730x730.png` | Fon rasmi (zaxira) |
| `EEG spectrum background 685x685.jpg` | Fon rasmi (zaxira) |
| `spektranaliz-eeg-logo*.svg` | Logotiplar |

---

## 5. Tez-tez uchraydigan savollar

**Fon rasmi chiqmayapti?**
Dastur fonni avval SVG (`svglib`/`reportlab`) orqali, keyin PNG/JPG zaxira
orqali ko'rsatadi. Barcha rasm fayllari `.exe` ichiga bundle qilingan, shuning
uchun o'rnatilgandan keyin ham ishlaydi.

**`.exe` hajmi katta?**
numpy/scipy/pandas kabi kutubxonalar tufayli normal holat. Hajmni kamaytirish
uchun `mne` ishlatilmaydi (uning o'rniga yengilroq `pyedflib`).

**EDF/BDF fayllar ochilmayapti?**
`pyedflib` o'rnatilganiga ishonch hosil qiling (`requirements.txt` da bor).

---

## 6. Qo'llab-quvvatlanadigan fayl formatlari

- **EDF / EDF+** (`.edf`)
- **BDF / BDF+** (`.bdf`)
- **CSV** (`.csv`) — vaqt ustuni avtomatik aniqlanadi

Natijada holatlar baholanadi: *Charchoq, Uyqusizlik, Normal, Fokus,
Xayajonlanish, Stress, Meditativ holat* — hamda chastota diapazonlari
(Delta, Theta, Alpha, Beta, Gamma) bo'yicha quvvat va spektral xususiyatlar.

> **Eslatma:** Natija spektral indekslarga asoslangan dasturiy baholash bo'lib,
> klinik tashxis sifatida ishlatilmaydi.
