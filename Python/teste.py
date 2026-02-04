import pandas as pd
import numpy as np

COLS = ["MQ2", "MQ7", "temperatura", "umidade"]

# Regras (ajuste se quiser)
MIN_LINHAS_OK = 300
MIN_LINHAS_IDEAL = 1000
MIN_STD = {"MQ2": 0.5, "MQ7": 0.5, "temperatura": 0.05, "umidade": 0.05}
Z_OUTLIER = 8.0
MAX_PCT_OUTLIER = 0.02  # 2%

df = pd.read_csv("dados_normais.csv")

print("shape:", df.shape)

# 1) Checa colunas
missing = [c for c in COLS if c not in df.columns]
if missing:
    print(f"❌ ERRO: colunas faltando: {missing}")
else:
    print("✅ Colunas OK:", COLS)

# 2) Converte p/ numérico (para detectar lixo/strings)
sub = df[COLS].copy() if not missing else None
if sub is not None:
    for c in COLS:
        sub[c] = pd.to_numeric(sub[c], errors="coerce")

    # 3) Linhas suficientes
    n = len(df)
    if n < MIN_LINHAS_OK:
        print(f"❌ ERRO: poucas linhas ({n}). Recomendado >= {MIN_LINHAS_OK} (ideal {MIN_LINHAS_IDEAL}+).")
    elif n < MIN_LINHAS_IDEAL:
        print(f"⚠️  AVISO: linhas OK ({n}), mas ideal é {MIN_LINHAS_IDEAL}+ para estabilidade.")
    else:
        print(f"✅ Linhas ideais: {n}")

    # 4) NaN / não numéricos
    na = sub.isna().sum()
    na_total = int(na.sum())
    if na_total > 0:
        cols_na = {k: int(v) for k, v in na.items() if v > 0}
        print(f"❌ ERRO: NaN/valores não numéricos após conversão: {cols_na}")
    else:
        print("✅ Sem NaN (nas colunas do modelo).")

    # 5) Describe + checks de “realismo”
    desc = sub.describe().T  # mean, std, min, max...
    print("\nDescribe (mean/std/min/max):")
    print(desc[["mean", "std", "min", "max"]].to_string(float_format=lambda x: f"{x:.6f}"))

    # 5a) Pouca variação / coluna travada
    for c in COLS:
        std = float(desc.loc[c, "std"]) if np.isfinite(desc.loc[c, "std"]) else 0.0
        if std == 0:
            print(f"❌ ERRO: coluna '{c}' travada (std=0).")
        elif std < MIN_STD.get(c, 0):
            print(f"⚠️  AVISO: pouca variação em '{c}' (std={std:.6f} < {MIN_STD[c]}).")

    # 5b) Outliers grosseiros (sinal de dado “quebrado”)
    z = (sub - sub.mean()) / sub.std(ddof=0)
    out_mask = z.abs().gt(Z_OUTLIER).any(axis=1)
    pct_out = float(out_mask.mean())
    if np.isfinite(pct_out) and pct_out > MAX_PCT_OUTLIER:
        print(f"⚠️  AVISO: muitos pontos extremos (|z|>{Z_OUTLIER}): {pct_out*100:.2f}% (> {MAX_PCT_OUTLIER*100:.2f}%).")
    else:
        print(f"✅ Extremos sob controle (|z|>{Z_OUTLIER}): {pct_out*100:.2f}%.")

# 6) Dtypes (original)
print("\nDtypes originais:\n", df.dtypes)

# 7) Resumo final (sem você ter que interpretar tudo)
if missing:
    print("\n🟥 RESULTADO: RUIM (faltam colunas).")
elif sub is None:
    print("\n🟥 RESULTADO: RUIM (não foi possível auditar).")
else:
    erros = []
    avisos = []

    n = len(df)
    if n < MIN_LINHAS_OK:
        erros.append("poucas linhas")
    if int(sub.isna().sum().sum()) > 0:
        erros.append("NaN/não numérico")
    desc = sub.describe().T
    for c in COLS:
        std = float(desc.loc[c, "std"]) if np.isfinite(desc.loc[c, "std"]) else 0.0
        if std == 0:
            erros.append(f"{c} travada")
        elif std < MIN_STD.get(c, 0):
            avisos.append(f"pouca variação em {c}")
    z = (sub - sub.mean()) / sub.std(ddof=0)
    pct_out = float(z.abs().gt(Z_OUTLIER).any(axis=1).mean())
    if np.isfinite(pct_out) and pct_out > MAX_PCT_OUTLIER:
        avisos.append("muitos extremos")

    if erros:
        print("\n🟥 RESULTADO: RUIM ->", "; ".join(erros))
    elif avisos:
        print("\n🟨 RESULTADO: OK COM RESSALVAS ->", "; ".join(avisos))
    else:
        print("\n🟩 RESULTADO: OK (dataset saudável para treinar).")
