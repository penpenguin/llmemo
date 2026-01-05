# Serena

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

config.toml
```toml
[mcp_servers.serena]
command = "uvx"
args = ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "codex"]
```

一度再起動すると使えるようになった

codexへプロンプトとして
```
Activate the current dir as project using serena
```

ダッシュボード  
http://localhost:24282/dashboard/
