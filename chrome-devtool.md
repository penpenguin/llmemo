# chrome-devtool

デスクトップにショートカットを作成する  
リンク先にオプションを追加  
ex.
```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome-devtools" --no-first-run --no-default-browser-check
```

Chromeのプロセスを全て落として、上記のショートカットを起動

確認
```cmd
netstat -ano | findstr :9222
curl 127.0.0.1:9222/json
```

WSLからホストのブラウザを使用するにはWSLの設定を変えて起動  
`%UserProfile%\.wslconfig`
```ini
[wsl2]
networkingMode=mirrored
localhostForwarding=true
dnsTunneling=true
```