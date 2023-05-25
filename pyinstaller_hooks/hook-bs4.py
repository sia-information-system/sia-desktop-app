from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('beautifulsoup4')
# datas, binaries, hiddenimports = collect_all('bs4')
