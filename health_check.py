import importlib

required_packages = [
    "aiogram",
    "MetaTrader5",
    "pillow",
    "pytesseract"
]

print("Running MT5 Bot Environment Health Check...\n")

missing = []
for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package} is installed.")
    except ImportError:
        print(f"❌ {package} is NOT installed.")
        missing.append(package)

if missing:
    print("\nSome packages are missing. Run:")
    print(f"pip install {' '.join(missing)}")
else:
    print("\nAll required packages are installed. You're ready to run the bot!")
