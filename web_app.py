from __future__ import annotations

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from turnstile_system import TurnstileSystem

system = TurnstileSystem()


def render_page(message: str = "") -> str:
    options = "\n".join(
        f'<option value="{gate}">{gate}</option>' for gate in TurnstileSystem.GATES
    )

    history_rows = "\n".join(
        "<tr>"
        f"<td>{event.timestamp:%d/%m/%Y %H:%M:%S}</td>"
        f"<td>{escape(event.badge_id)}</td>"
        f"<td>{escape(event.gate_id)}</td>"
        f"<td>{escape(event.direction)}</td>"
        "</tr>"
        for event in reversed(system.history())
    )

    if not history_rows:
        history_rows = '<tr><td colspan="4">Sem registros ainda.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Controle de Catracas</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f3f4f6; margin: 0; padding: 24px; }}
    .container {{ max-width: 980px; margin: 0 auto; }}
    .card {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,.08); margin-bottom: 16px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }}
    label {{ display: block; font-size: 14px; margin-bottom: 6px; color: #374151; }}
    input, select, button {{ width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; }}
    .actions {{ display: flex; gap: 12px; margin-top: 12px; }}
    .btn-entrada {{ background: #16a34a; color: white; border: none; cursor: pointer; }}
    .btn-saida {{ background: #dc2626; color: white; border: none; cursor: pointer; }}
    .stats {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .pill {{ background: #0f172a; color: #fff; padding: 10px 14px; border-radius: 999px; font-size: 14px; }}
    .message {{ padding: 10px; border-radius: 8px; background: #dbeafe; color: #1e3a8a; margin-bottom: 12px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; border-bottom: 1px solid #e2e8f0; padding: 8px; font-size: 14px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>Sistema de leitura de catracas (8 catracas)</h1>
      {f'<div class="message">{escape(message)}</div>' if message else ''}
      <div class="stats">
        <span class="pill">Pessoas no ambiente: {system.current_occupancy()}</span>
        <span class="pill">Catracas ativas: {len(TurnstileSystem.GATES)}</span>
      </div>
      <form method="post">
        <div class="grid">
          <div>
            <label for="badge_id">Crachá</label>
            <input id="badge_id" name="badge_id" placeholder="Ex.: A123" required />
          </div>
          <div>
            <label for="gate_id">Catraca</label>
            <select id="gate_id" name="gate_id">{options}</select>
          </div>
        </div>
        <div class="actions">
          <button class="btn-entrada" name="direction" value="entrada" type="submit">Registrar Entrada</button>
          <button class="btn-saida" name="direction" value="saida" type="submit">Registrar Saída</button>
        </div>
      </form>
    </div>

    <div class="card">
      <h2>Últimos registros</h2>
      <table>
        <thead>
          <tr>
            <th>Data/Hora</th>
            <th>Crachá</th>
            <th>Catraca</th>
            <th>Direção</th>
          </tr>
        </thead>
        <tbody>
          {history_rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


class TurnstileHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        content = render_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body)

        badge_id = form.get("badge_id", [""])[0]
        gate_id = form.get("gate_id", [""])[0]
        direction = form.get("direction", [""])[0]

        message = ""
        try:
            event = system.register_read(badge_id, gate_id, direction)
            message = (
                f"Leitura registrada: {event.badge_id} | {event.gate_id} | {event.direction}"
            )
        except ValueError as error:
            message = f"Erro: {error}"

        content = render_page(message).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), TurnstileHandler)
    print("Servidor disponível em http://localhost:8000")
    server.serve_forever()
