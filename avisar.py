"""Envia no Telegram o aviso das ações de higienização do dia seguinte.

Lê agenda.csv (separado por ponto e vírgula, datas no formato dd/mm/aaaa).
Variáveis de ambiente:
  TELEGRAM_TOKEN    token do bot (criado no @BotFather)
  TELEGRAM_CHAT_ID  id do chat que vai receber (pode ser mais de um, separados por vírgula)
  MODO              "vespera" (padrão): avisa se houver ação amanhã
                    "proxima": envia agora a próxima ação da agenda (para testar)
  DATA_HOJE         opcional, dd/mm/aaaa, para simular outro dia
  DRY_RUN           opcional, "1" mostra a mensagem sem enviar
"""
import csv, html, json, os, sys, urllib.parse, urllib.request
from collections import OrderedDict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def ler_agenda():
    erros, linhas = [], []
    with open(os.path.join(AQUI, "agenda.csv"), encoding="utf-8-sig", newline="") as f:
        primeira = f.readline(); f.seek(0)
        sep = ";" if primeira.count(";") >= primeira.count(",") else ","
        for n, r in enumerate(csv.DictReader(f, delimiter=sep), start=2):
            r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
            if not any(r.values()):
                continue
            try:
                r["_data"] = datetime.strptime(r["data"], "%d/%m/%Y").date()
            except Exception:
                erros.append(f"linha {n}: data inválida '{r.get('data')}' (use dd/mm/aaaa)")
                continue
            linhas.append(r)
    if erros:
        print("Erros na agenda.csv:\n  " + "\n  ".join(erros))
        sys.exit(1)
    return linhas


def montar(acoes, titulo, dia):
    e = html.escape
    txt = [f"⚠️ <b>{e(titulo)}</b>", f"📅 {DIAS[dia.weekday()]}, {dia:%d/%m/%Y}"]
    grupos = OrderedDict()
    for a in acoes:
        grupos.setdefault((a.get("municipio", ""), a.get("acao", ""), a.get("horario", "")), []).append(a)
    for (mun, num, hora), itens in grupos.items():
        bairro = itens[0].get("bairro")
        cab = f"\n📍 <b>{e(mun)}</b>" + (f" – {e(bairro)}" if bairro else "")
        if num:
            cab += f" | {e(num)}ª ação"
        if hora:
            cab += f" | 🕗 {e(hora)}"
        txt.append(cab)
        for a in itens:
            linha = f"• <b>{e(a.get('logradouro', ''))}</b>"
            if a.get("trecho"):
                linha += f"\n   {e(a['trecho'])}"
            if a.get("postes"):
                linha += f" ({e(a['postes'])} postes)"
            txt.append(linha)
            lat, lon = a.get("latitude"), a.get("longitude")
            nome = a.get("ponto_encontro") or "Ponto de encontro"
            if lat and lon:
                url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"{lat},{lon}")
                txt.append(f'   🚩 <a href="{url}">{e(nome)}</a>')
            elif a.get("ponto_encontro"):
                txt.append(f"   🚩 {e(nome)}")
    return "\n".join(txt)


def enviar(texto):
    if os.environ.get("DRY_RUN") == "1":
        print(texto); return
    token = os.environ["TELEGRAM_TOKEN"].strip()
    for chat in os.environ["TELEGRAM_CHAT_ID"].split(","):
        dados = urllib.parse.urlencode({"chat_id": chat.strip(), "text": texto, "parse_mode": "HTML",
                                        "disable_web_page_preview": "true"}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=dados)
        with urllib.request.urlopen(req, timeout=30) as resp:
            if not json.load(resp).get("ok"):
                sys.exit("Telegram recusou a mensagem")
    print("Mensagem enviada.")


def main():
    hoje = (datetime.strptime(os.environ["DATA_HOJE"], "%d/%m/%Y").date() if os.environ.get("DATA_HOJE")
            else datetime.now(ZoneInfo("America/Sao_Paulo")).date())
    agenda = ler_agenda()
    modo = os.environ.get("MODO", "vespera").strip().lower()
    if modo == "proxima":
        futuras = sorted({a["_data"] for a in agenda if a["_data"] >= hoje})
        if not futuras:
            enviar("✅ Não há ações futuras na agenda."); return
        dia = futuras[0]
        enviar(montar([a for a in agenda if a["_data"] == dia], "Teste: próxima ação da agenda", dia))
        return
    amanha = hoje + timedelta(days=1)
    acoes = [a for a in agenda if a["_data"] == amanha]
    if not acoes:
        print(f"Nenhuma ação em {amanha:%d/%m/%Y}. Nada a enviar."); return
    enviar(montar(acoes, "Amanhã tem ação de higienização", amanha))


if __name__ == "__main__":
    main()
