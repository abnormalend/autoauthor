def required(N, caps, G):
    """Avg the uncapped dimensions must reach, per number of caps firing."""
    need = int(G * N) + 1                      # strict >, integer scores
    out = []
    for k in range(1, len(caps) + 1):
        worst = sorted(caps)[:k]               # the k lowest caps co-fire
        rest = N - k
        out.append(float('inf') if rest <= 0 else (need - sum(worst)) / rest)
    return need, out

def max_gate(N, caps, k1=8.0, k2=8.0):
    """Highest gate where 1 cap is reachable and 2 need no 9."""
    best = None
    for g in range(40, 91):                    # 4.0 .. 9.0 in .1 steps
        G = g / 10
        _, req = required(N, caps, G)
        ok = (len(req) < 1 or req[0] <= k1) and (len(req) < 2 or req[1] <= k2)
        if ok: best = G
    return best

for label, N, caps in [
    ("fantasy  (extended, today)", 5, [6, 6]),
    ("fantasy  (as shipped pre-fix)", 5, [4, 4, 6]),
    ("romantasy(extended)", 6, [6, 6, 6]),
    ("fantasy  (compressed, 2 dims)", 2, [6]),
    ("romance  (compressed, 3 dims)", 3, [6, 6]),
]:
    need, req = required(N, caps, 7.0)
    g = max_gate(N, caps)
    print(f"{label:32} N={N} caps={str(caps):12} "
          f"at 7.0 need {[round(r,2) for r in req]}  -> max gate {g}")
