#!/usr/bin/env python3
"""Coletor dos sinais automáticos dos 5 futuros: Python puro, sem chave e sem API paga.

Baixa dados públicos, calcula os sinais e grava:
  estado/sinais.md       tabela para você e para o agente lerem
  estado/sinais.json     os valores desta coleta
  estado/historico.csv   uma linha por sinal por coleta (para ver a tendência)

Uso:
  python3 coletor/coleta.py                  # coleta tudo (usa o cache se o arquivo for recente)
  python3 coletor/coleta.py --so epoch       # só as fontes leves (Epoch)
  python3 coletor/coleta.py --dados DIR      # usa arquivos locais (testes), sem internet

Fontes (ver cenarios/sinais.yaml): Epoch AI (CC BY 4.0), Anthropic Economic Index (MIT),
AI Incident Database (backup semanal). Os limites são PROPOSTAS para calibrar, não previsões.
"""
import argparse, csv, io, json, re, sys, tarfile, time, urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
KIT = AQUI.parent
UA = {"User-Agent": "Mozilla/5.0 (cinco-futuros coletor; +https://github.com/inematds/cinco-futuros)"}
csv.field_size_limit(10**9)

URL = {
    "epoch_modelos": "https://epoch.ai/data/all_ai_models.csv",
    "epoch_clusters": "https://epoch.ai/data/gpu_clusters.csv",
    "aei_lista": "https://huggingface.co/api/datasets/Anthropic/EconomicIndex",
    "aei_base": "https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/",
    "aiid_pagina": "https://incidentdatabase.ai/research/snapshots/",
}

# limite de cada sinal automático: (função que diz se passou, texto do limite, cenários que ele empurra)
LIMIAR = {
    "compute-fronteira": (lambda v: v >= 1e27, ">= 1e27 FLOP", "1 extinção ↑ · 3 governo ↑"),
    "lacuna-aberto-fechado": (lambda v: v > 30, "> 30x (poder concentrado)", "2 zoológico ↑ · 3 governo ↑ · 5 utopia ↓"),
    "corrida-eua-china": (lambda v: v < 3, "< 3x (corrida apertada)", "1 extinção ↑"),
    "concentracao-clusters": (lambda v: v > 60, "> 60%", "2 zoológico ↑ · 3 governo ↑"),
    "automacao-uso": (lambda v: v > 50, "> 50% automação", "4 paraíso ↑ · 2 zoológico ↑ · 5 utopia ↓"),
    "incidentes-ia": (lambda v: v > 1.5, "> 1,5x a média de 12 meses", "1 extinção ↑ · 3 governo ↑"),
}
NOME = {
    "compute-fronteira": "Maior treino de IA (12 meses)",
    "lacuna-aberto-fechado": "Fechado ÷ aberto (compute)",
    "corrida-eua-china": "EUA ÷ China (compute)",
    "concentracao-clusters": "3 maiores donos nos 20 maiores clusters",
    "automacao-uso": "Conversas de automação (Economic Index)",
    "incidentes-ia": "Incidentes com IA (3 meses ÷ 12 meses)",
}
MANUAIS = ["horizonte-agentes", "ritmo-ai2027", "emprego-jovens", "emprego-brasil", "regulacao-adiada",
           "governanca-global", "renda-basica"]
PESSOAIS = ["delegacao-pessoal", "habilidade-propria", "parceria-ia"]


# ---------- download com cache ----------
def baixa(url, destino, max_horas=24):
    destino = Path(destino)
    if destino.exists() and time.time() - destino.stat().st_mtime < max_horas * 3600:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".parcial")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(tmp, "wb") as f:
        while bloco := r.read(1 << 20):
            f.write(bloco)
    tmp.replace(destino)
    return destino


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


# ---------- Epoch: modelos ----------
def sinais_epoch_modelos(caminho, hoje):
    ini = (hoje - timedelta(days=365)).isoformat()
    linhas = [r for r in csv.DictReader(open(caminho, encoding="utf-8"))
              if r.get("Publication date", "") >= ini and num(r.get("Training compute (FLOP)"))]
    if not linhas:
        return {}

    def maior(filtro):
        c = [r for r in linhas if filtro(r)]
        return max(c, key=lambda r: num(r["Training compute (FLOP)"])) if c else None

    aberto = lambda r: r.get("Model accessibility", "").startswith("Open weights")
    top = maior(lambda r: True)
    top_aberto = maior(aberto)
    top_fechado = maior(lambda r: not aberto(r))
    top_eua = maior(lambda r: "United States" in r.get("Country (of organization)", ""))
    top_china = maior(lambda r: "China" in r.get("Country (of organization)", ""))
    fl = lambda r: num(r["Training compute (FLOP)"])
    rot = lambda r: f'{r["Model"]} ({r["Organization"]}, {r["Publication date"]})'
    out = {"compute-fronteira": (fl(top), rot(top))}
    if top_aberto and top_fechado:
        out["lacuna-aberto-fechado"] = (fl(top_fechado) / fl(top_aberto), f"fechado {rot(top_fechado)} · aberto {rot(top_aberto)}")
    if top_eua and top_china:
        out["corrida-eua-china"] = (fl(top_eua) / fl(top_china), f"EUA {rot(top_eua)} · China {rot(top_china)}")
    return out


# ---------- Epoch: clusters ----------
def sinais_epoch_clusters(caminho):
    linhas = []
    for r in csv.DictReader(open(caminho, encoding="utf-8")):
        h = num(r.get("H100 equivalents"))
        if not h or r.get("Status") != "Existing" or str(r.get("Exclude", "")).strip().lower() in ("true", "yes", "1", "checked"):
            continue
        if str(r.get("Possible Duplicate", "")).strip().lower() in ("true", "yes", "1", "checked"):
            continue
        linhas.append((h, (r.get("Owner") or "?").split(",")[0].strip()))
    top = sorted(linhas, reverse=True)[:20]
    if not top:
        return {}
    por_dono = defaultdict(float)
    for h, dono in top:
        por_dono[dono] += h
    tot = sum(por_dono.values())
    tres = sorted(por_dono.items(), key=lambda x: -x[1])[:3]
    return {"concentracao-clusters": (100 * sum(v for _, v in tres) / tot, " · ".join(d for d, _ in tres))}


# ---------- Anthropic Economic Index ----------
def aei_mais_recente(lista_json):
    nomes = [s["rfilename"] for s in json.loads(Path(lista_json).read_text())["siblings"]]
    c = sorted(n for n in nomes if re.fullmatch(r"release_\d{4}_\d{2}_\d{2}/data/aei_claude_ai_[\d-]+\.csv", n))
    return c[-1] if c else None


def sinais_aei(caminho, release=""):
    melhor = {}
    for r in csv.DictReader(open(caminho, encoding="utf-8")):
        if r["category_name"] == "overall" and r["metric_id"] == "collaboration_bucket_automation_pct" \
                and r["geo_id"] in ("GLOBAL", "BR"):
            if r["date_start"] >= melhor.get(r["geo_id"], ("",))[0]:
                melhor[r["geo_id"]] = (r["date_start"], float(r["value"]))
    if "GLOBAL" not in melhor:
        return {}
    d, v = melhor["GLOBAL"]
    extra = f"mundo, mês de {d[:7]}" + (f" · Brasil {melhor['BR'][1]:.1f}%" if "BR" in melhor else "") + (f" · {release}" if release else "")
    return {"automacao-uso": (v, extra)}


# ---------- AI Incident Database ----------
def aiid_mais_recente(html):
    urls = re.findall(r'https://[^"\s]+?backup-(\d{14})\.tar\.bz2', html)
    if not urls:
        return None
    ultimo = max(urls)
    return re.search(rf'https://[^"\s]+?backup-{ultimo}\.tar\.bz2', html).group(0)


def incidentes_csv_do_backup(tar_bz2, destino):
    with tarfile.open(tar_bz2, mode="r:bz2") as t:
        for m in t:
            if m.name.endswith("/incidents.csv"):
                Path(destino).write_bytes(t.extractfile(m).read())
                return destino
    raise RuntimeError("incidents.csv não está no backup")


def sinais_aiid(incidents_csv, hoje):
    """Incidentes por mês do incidente. Os 2 meses mais recentes ficam de fora (registro chega atrasado)."""
    por_mes = defaultdict(int)
    for r in csv.DictReader(open(incidents_csv, encoding="utf-8")):
        if re.match(r"\d{4}-\d{2}", r.get("date", "")):
            por_mes[r["date"][:7]] += 1

    def mes(k):  # k meses antes do mês atual
        y, m = hoje.year, hoje.month - k
        while m <= 0:
            y, m = y - 1, m + 12
        return f"{y}-{m:02d}"

    tres = [por_mes[mes(k)] for k in range(3, 6)]
    doze = [por_mes[mes(k)] for k in range(3, 15)]
    if not sum(doze):
        return {}
    v = (sum(tres) / 3) / (sum(doze) / 12)
    return {"incidentes-ia": (v, f"{sum(tres)} incidentes em {mes(5)}..{mes(3)}; média de 12 meses {sum(doze) / 12:.1f}/mês")}


# ---------- saída ----------
def formata(sid, v):
    if sid == "compute-fronteira":
        return f"{v:.2e} FLOP"
    if sid in ("lacuna-aberto-fechado", "corrida-eua-china", "incidentes-ia"):
        return f"{v:.1f}x"
    return f"{v:.1f}%"


def grava(estado, valores, erros, hoje):
    estado.mkdir(parents=True, exist_ok=True)
    js = {sid: {"valor": v, "detalhe": d, "passou": LIMIAR[sid][0](v), "limiar": LIMIAR[sid][1]}
          for sid, (v, d) in valores.items()}
    (estado / "sinais.json").write_text(json.dumps({"data": hoje.isoformat(), "sinais": js, "erros": erros},
                                                   ensure_ascii=False, indent=1))
    hist = estado / "historico.csv"
    novo = not hist.exists()
    with open(hist, "a", newline="") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["data", "sinal", "valor", "passou"])
        for sid, x in js.items():
            w.writerow([hoje.isoformat(), sid, x["valor"], x["passou"]])

    L = [f"# Sinais dos 5 futuros: coleta de {hoje.strftime('%d/%m/%Y')}", "",
         "Gerado por `coletor/coleta.py`. Os limites são propostas para calibrar, não previsões. "
         "O agente lê esta tabela, preenche os sinais manuais e atualiza `termometro.md`.", "",
         "## Automáticos", "", "| Sinal | Valor | Limite | Passou? | Empurra | Detalhe |", "|---|---|---|---|---|---|"]
    for sid in LIMIAR:
        if sid in js:
            x = js[sid]
            L.append(f"| {NOME[sid]} (`{sid}`) | {formata(sid, x['valor'])} | {x['limiar']} | "
                     f"{'**SIM**' if x['passou'] else 'não'} | {LIMIAR[sid][2]} | {x['detalhe']} |")
        else:
            L.append(f"| {NOME[sid]} (`{sid}`) | — | {LIMIAR[sid][1]} | — | {LIMIAR[sid][2]} | não coletado: {erros.get(sid, 'fonte não pedida')} |")
    L += ["", "## Manuais: o agente lê a fonte e anota (ver `cenarios/sinais.yaml`)", ""]
    L += [f"- `{s}`: " for s in MANUAIS]
    L += ["", "## Pessoais: você responde na revisão semanal", ""]
    L += [f"- `{s}`: " for s in PESSOAIS]
    (estado / "sinais.md").write_text("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estado", default=str(KIT / "estado"))
    ap.add_argument("--so", default="epoch,aei,aiid", help="fontes: epoch, aei, aiid (vírgula)")
    ap.add_argument("--dados", help="pasta com arquivos locais (epoch_modelos.csv, epoch_clusters.csv, aei.csv, incidents.csv)")
    ap.add_argument("--hoje", help="AAAA-MM-DD (testes)")
    a = ap.parse_args(argv)
    hoje = date.fromisoformat(a.hoje) if a.hoje else date.today()
    estado = Path(a.estado)
    cache = estado / "cache"
    so = set(a.so.split(","))
    valores, erros = {}, {}
    local = Path(a.dados) if a.dados else None

    def tenta(ids, func):
        try:
            valores.update(func())
        except Exception as e:  # uma fonte fora do ar não derruba as outras
            for i in ids:
                erros[i] = f"{type(e).__name__}: {str(e)[:120]}"
            print(f"!! {ids}: {e}", file=sys.stderr)

    if "epoch" in so:
        tenta(["compute-fronteira", "lacuna-aberto-fechado", "corrida-eua-china"], lambda: sinais_epoch_modelos(
            local / "epoch_modelos.csv" if local else baixa(URL["epoch_modelos"], cache / "epoch_modelos.csv"), hoje))
        tenta(["concentracao-clusters"], lambda: sinais_epoch_clusters(
            local / "epoch_clusters.csv" if local else baixa(URL["epoch_clusters"], cache / "epoch_clusters.csv")))
    if "aei" in so:
        def aei():
            if local:
                return sinais_aei(local / "aei.csv")
            nome = aei_mais_recente(baixa(URL["aei_lista"], cache / "aei_lista.json"))
            arq = cache / Path(nome).name  # o nome muda a cada release: baixa só quando sai release nova
            return sinais_aei(baixa(URL["aei_base"] + nome, arq, max_horas=24 * 365), nome.split("/")[0])
        tenta(["automacao-uso"], aei)
    if "aiid" in so:
        def aiid():
            if local:
                return sinais_aiid(local / "incidents.csv", hoje)
            pag = baixa(URL["aiid_pagina"], cache / "aiid_snapshots.html")
            url = aiid_mais_recente(pag.read_text(errors="ignore"))
            inc = cache / f"incidents-{re.search(r'backup-(\d+)', url).group(1)}.csv"
            if not inc.exists():
                tar = baixa(url, cache / "aiid_backup.tar.bz2", max_horas=24 * 7)
                incidentes_csv_do_backup(tar, inc)
                tar.unlink()
            return sinais_aiid(inc, hoje)
        tenta(["incidentes-ia"], aiid)

    grava(estado, valores, erros, hoje)
    passou = [s for s, (v, _) in valores.items() if LIMIAR[s][0](v)]
    print(f"Terminei: {len(valores)} sinais coletados em {estado / 'sinais.md'}"
          + (f" — passaram do limite: {', '.join(passou)}" if passou else " — nenhum passou do limite")
          + (f" — falharam: {', '.join(erros)}" if erros else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
