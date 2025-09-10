# --- ADD near the top with other imports ---
from typing import Tuple

# --- ADD below BASE/UA ---
LATEST = f"{BASE}/latest"

def fetch_latest() -> Dict[str, Any]:
    r = requests.get(LATEST, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()

def get_top_traded_item_ids(n: int = 100, prefer: str = "high") -> List[int]:
    """
    Rank items by recent trade volume from /latest and return top-N item_ids.
    prefer: "high" uses highPriceVolume; "low" uses lowPriceVolume; "sum" uses both.
    """
    data = fetch_latest()
    # shape: {"data": { "554": {"high":..., "highTime":..., "highPriceVolume":..., "lowPriceVolume":...}, ...}}
    payload = data.get("data", {})
    ranked: List[Tuple[int, int]] = []
    for k, v in payload.items():
        try:
            item_id = int(k)
        except ValueError:
            continue
        hv = int(v.get("highPriceVolume") or 0)
        lv = int(v.get("lowPriceVolume") or 0)
        score = hv if prefer == "high" else lv if prefer == "low" else (hv + lv)
        ranked.append((item_id, score))
    ranked.sort(key=lambda x: x[1], reverse=True)
    # take top-N with nonzero volume
    top_ids = [iid for iid, vol in ranked if vol > 0][:n]
    return top_ids

# --- CHANGE argparse to add options (replace your existing --timestep line block with this) ---
ap.add_argument("--timestep", default="24h", choices=["5m","1h","6h","24h"],
                help="Timeseries granularity per OSRS Wiki API")
ap.add_argument("--top-n", type=int, default=100,
                help="When --items=topN, number of most-traded items to pull (default 100)")
ap.add_argument("--volume-pref", choices=["high","low","sum"], default="sum",
                help="Rank by highPriceVolume, lowPriceVolume, or sum (default sum)")

# --- REPLACE resolve_items_arg with this version ---
def resolve_items_arg(items_arg: str, mapping: List[Dict[str, Any]], top_n: int, vol_pref: str) -> List[int]:
    """
    Accepts:
      - 'topN' (case-insensitive)  -> pick top_n from /latest
      - 'top###' (e.g., top500)    -> pick that many from /latest
      - comma-separated ids/names  -> resolve via mapping
    """
    token = (items_arg or "").strip().lower()

    # topN keyword
    if token == "topn":
        return get_top_traded_item_ids(n=top_n, prefer=vol_pref)

    # top### pattern
    if token.startswith("top"):
        try:
            n = int(token[3:])
            if n > 0:
                return get_top_traded_item_ids(n=n, prefer=vol_pref)
        except Exception:
            pass  # fall through to manual parsing

    # explicit list (ids or names)
    ids: List[int] = []
    names_to_id = {m["name"].lower(): m["id"] for m in mapping if "name" in m and "id" in m}
    for part in token.split(","):
        p = part.strip()
        if not p:
            continue
        if p.isdigit():
            ids.append(int(p))
        else:
            if p in names_to_id:
                ids.append(int(names_to_id[p]))
            else:
                print(f"[warn] Could not resolve item name: {p}", file=sys.stderr)
    # de-dup preserve order
    seen = set()
    uniq = []
    for i in ids:
        if i not in seen:
            uniq.append(i)
            seen.add(i)
    return uniq

# --- UPDATE call site where you currently do: ids = resolve_items_arg(args.items, mapping) ---
ids = resolve_items_arg(args.items, mapping, args.top_n, args.volume_pref)
