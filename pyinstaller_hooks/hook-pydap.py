from PyInstaller.utils.hooks import collect_all

# pydap.responses.ascii
datas, binaries, hiddenimports = collect_all('pydap')
