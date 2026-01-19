import subprocess
import platform
from datetime import datetime
import time
import json
import os

ARQUIVO_TXT = "lojas.txt"
RELATORIO_HTML = "index.html"
STATE_FILE = "offline_state.json"
INTERVALO = 30 # segundos


def ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout = "1000" if platform.system().lower() == "windows" else "1"

    comando = ["ping", param, "1", "-w", timeout, ip]

    try:
        inicio = time.time()
        resultado = subprocess.run(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        fim = time.time()

        if resultado.returncode == 0:
            latencia = int((fim - inicio) * 1000)
            return True, latencia
        return False, None
    except:
        return False, None



# 🔹 Carrega estado offline persistente
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        offline_state = json.load(f)
else:
    offline_state = {}


def offline_duration(k):
    if k not in offline_state:
        return ""

    inicio = offline_state[k]
    segundos = int(time.time() - inicio)

    if segundos < 60:
        return "🕒 agora mesmo"

    minutos = segundos // 60
    if minutos < 60:
        return f"🕒 há {minutos} min"

    horas = minutos // 60
    minutos_restantes = minutos % 60

    if horas < 24:
        return f"🕒 há {horas}h {minutos_restantes:02d}min"

    dias = horas // 24
    horas_restantes = horas % 24
    return f"🕒 há {dias}d {horas_restantes}h"


try:
    while True:
        cards = []
        online = servidor_off = link_off = 0
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with open(ARQUIVO_TXT, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue

                k, nome, ip_link, ip_servidor = linha.split(";")

                servidor_ok, latencia = ping(ip_servidor)

                if servidor_ok:
                    status = "🟢 Online"
                    detalhe = "Servidor respondeu"
                    card_class = "online"
                    prioridade = 2
                    online += 1
                    offline_state.pop(k, None)

                else:
                    link_ok, _ = ping(ip_link)

                    if link_ok:
                        status = "🟠 Servidor Offline"
                        detalhe = "Link OK / Servidor sem resposta"
                        card_class = "server-off"
                        prioridade = 1
                        servidor_off += 1
                    else:
                        status = "🔴 Link Offline"
                        detalhe = "Link e servidor sem resposta"
                        card_class = "link-off"
                        prioridade = 0
                        link_off += 1

                    if k not in offline_state:
                        offline_state[k] = time.time()

                latencia_html = f"⏱️ {latencia} ms" if latencia else "⏱️ --"
                offline_txt = offline_duration(k)

                cards.append({
                    "prioridade": prioridade,
                    "html": f"""
                    <div class="card {card_class}">
                        <div class="card-header">
                            <span class="title">{k} - {nome}</span>
                            <span class="latency">{latencia_html}</span>
                        </div>
                        <div class="ip">🖥 Servidor: {ip_servidor}</div>
                        <div class="ip">🌐 Link: {ip_link}</div>
                        <div class="status">{status}</div>
                        <div class="offline">{offline_txt}</div>
                        <div class="detail">{detalhe}</div>
                    </div>
                    """
                })

        # 🔼 Offline sobe para o topo
        cards.sort(key=lambda x: x["prioridade"])
        cards_html = "".join(card["html"] for card in cards)

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(offline_state, f)

        html = f"""
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="{INTERVALO}">
<title>Network Monitoring</title>

<style>
body {{
    margin: 0;
    font-family: Segoe UI, Arial, sans-serif;
    background: radial-gradient(circle at top, #020617, #0f172a);
    color: #e5e7eb;
}}

.controls {{
    display: flex;
    gap: 10px;
    padding: 15px;
    flex-wrap: wrap;
    align-items: center;
    background: #020617;
    border-bottom: 1px solid #1e293b;
}}

input {{
    padding: 10px;
    border-radius: 8px;
    border: none;
    background: #0f172a;
    color: #e5e7eb;
    min-width: 220px;
}}

button {{
    padding: 10px 16px;
    border: none;
    border-radius: 999px;
    cursor: pointer;
    font-weight: bold;
    background: linear-gradient(135deg, #1e293b, #020617);
    color: #e5e7eb;
}}

button.active {{
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
}}

.grid {{
    padding: 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
}}

.card {{
    border-radius: 18px;
    padding: 20px;
    background: linear-gradient(135deg, #020617, #020617 40%);
    box-shadow: 0 10px 30px rgba(0,0,0,.35);
    border: 1px solid #1e293b;
    transition: background 0.3s ease, border-color 0.3s ease;
}}

.card.online {{
    background: linear-gradient(135deg, #064e3b, #020617 65%);
    border-color: #22c55e;
}}

.card.server-off {{
    background: linear-gradient(135deg, #78350f, #020617 65%);
    border-color: #f59e0b;
}}

.card.link-off {{
    background: linear-gradient(135deg, #7f1d1d, #020617 65%);
    border-color: #ef4444;
}}

@keyframes blink {{
    0% {{ box-shadow: 0 0 6px #ef4444; }}
    50% {{ box-shadow: 0 0 20px #ef4444; }}
    100% {{ box-shadow: 0 0 6px #ef4444; }}
}}

.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.latency {{
    white-space: nowrap;
    font-weight: bold;
}}

.offline {{
    margin-top: 6px;
    font-size: 14px;
    opacity: .85;
}}

.title {{ font-weight: 700; font-size: 16px; }}
.ip {{ font-size: 14px; opacity: .85; }}
.status {{ margin-top: 15px; font-weight: bold; }}
.detail {{ font-size: 13px; opacity: .7; }}
</style>

<script>
function search() {{
    let q = document.getElementById("search").value.toLowerCase();
    document.querySelectorAll(".card").forEach(card => {{
        card.style.display = card.innerText.toLowerCase().includes(q) ? "" : "none";
    }});
}}

function filterStatus(status, btn) {{
    document.querySelectorAll("button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    document.querySelectorAll(".card").forEach(card => {{
        card.style.display = status === "all" || card.classList.contains(status) ? "" : "none";
    }});
}}
</script>
</head>

<body>

<div class="controls">
    <input id="search" placeholder="🔍 Buscar loja..." onkeyup="search()">

    <button class="active" onclick="filterStatus('all', this)">Todos</button>
    <button onclick="filterStatus('online', this)">🟢 Online</button>
    <button onclick="filterStatus('server-off', this)">🟠 Servidor Offline</button>
    <button onclick="filterStatus('link-off', this)">🔴 Link Offline</button>

    <strong style="margin-left:auto;">🟢 {online} | 🟠 {servidor_off} | 🔴 {link_off}</strong>
    <span style="opacity:.6;">Atualizado: {data_hora}</span>
</div>

<div class="grid">
{cards_html}
</div>

</body>
</html>
"""

        with open(RELATORIO_HTML, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[{data_hora}] Relatório atualizado")
        time.sleep(INTERVALO)

except KeyboardInterrupt:
    print("Monitoramento encerrado pelo usuário.")
