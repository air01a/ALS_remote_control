cd ..
pyinstaller -i src\\resources\\als_logo.ico -D -n als --windowed  --add-data "src\\resources\\qt.conf;." --upx-dir C:\Users\eniquet\dev\upx-4.1.0-win64 --paths src\\  src\\start.py
pyinstaller -i src\\resources\\als_logo.ico -F -n alscontrol --console --upx-dir C:\Users\eniquet\dev\upx-4.1.0-win64 src\\als\\als_remote_client.py