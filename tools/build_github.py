#!/usr/bin/env python3
"""Build the GitHub copy of ACIS Security Analysis from the live platform.

Inputs
  platform/index.html     the page exactly as published in Claude
  <export>/<collection>/<doc_id>.json   one file per database document

Outputs
  index.html              read-only GitHub version (loads data/snapshot.json, local assets, browser downloads)
  data/snapshot.json      every record; rewritten only when the data actually changed

Usage
  python3 tools/build_github.py --export EXPORT_DIR          build
  python3 tools/build_github.py --export EXPORT_DIR --assets list the asset ids that still need downloading
                                                              into assets/files/ (one per line)
"""
import argparse, glob, json, os, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTIONS = ["news", "countries", "briefs", "forecasts", "weeks", "weekparts", "meta", "reviews"]
# meta documents that are only short-lived locks
SKIP_META = {"lock", "watch", "morning"}
KNOWN = {
    "5be0d5253729ae85226128d7500f2982": "assets/logo-government-of-dubai.png",
    "b1dcdf8a583754ef7bfec3a744dc1ff8": "assets/logo-acis.png",
    "5438a066ac0b2abe6f9b3b0d7851c092": "assets/logo-dubai-police.png",
    "1122195bbfbc74b58778b70a2d8b2339": "assets/app-icon.png",
    "bbc1c4ba434efe257939f45b4774f7f0": "assets/app-icon-previous.png",
    "734c32606cfc02dc09c0a64d0f967153": "assets/fonts/29LT-Bukra-Regular.otf",
    "6a9980a112c35901d776637443351268": "assets/fonts/29LT-Bukra-Bold.otf",
}
BLOB = re.compile(r"/_blob/([0-9a-f]{32})")


def load(export, col):
    out = {}
    for f in sorted(glob.glob(os.path.join(export, col, "*.json"))):
        doc_id = os.path.basename(f)[:-5]
        if col == "meta" and doc_id in SKIP_META:
            continue
        with open(f, encoding="utf-8") as fh:
            out[doc_id] = json.load(fh)
    return out


def snapshot(export):
    data = {c: load(export, c) for c in COLLECTIONS}
    return {
        "source": "ACIS Security Analysis (Claude artifact)",
        "news": [{"id": k, **v} for k, v in data["news"].items()],
        "countries": data["countries"],
        "briefs": data["briefs"],
        "forecasts": [{"id": k, **v} for k, v in data["forecasts"].items()],
        "weeks": data["weeks"],
        "weekparts": data["weekparts"],
        "meta": data["meta"],
        "reviews": data["reviews"],
    }


def needed_assets(page, snap):
    ids = set(BLOB.findall(page))
    for n in snap["news"]:
        for a in n.get("attachments") or []:
            if isinstance(a, dict) and re.fullmatch(r"[0-9a-f]{32}", str(a.get("id", ""))):
                ids.add(a["id"])
    have = {os.path.basename(p).split(".")[0] for p in glob.glob(os.path.join(ROOT, "assets", "files", "*"))}
    return sorted(i for i in ids if i not in KNOWN and i not in have)


def asset_path(blob_id):
    if blob_id in KNOWN:
        return KNOWN[blob_id]
    hits = glob.glob(os.path.join(ROOT, "assets", "files", blob_id + ".*"))
    return "assets/files/" + os.path.basename(hits[0]) if hits else "assets/files/" + blob_id


def rep(g, old, new):
    if g.count(old) != 1:
        sys.exit(f"build_github: expected exactly one match for: {old[:70]!r} (found {g.count(old)})")
    return g.replace(old, new)


SNAPCODE = r'''/* ---------- GitHub copy: read-only snapshot when the page runs outside Claude ---------- */
Object.assign(T.en,{snapNote:"Read-only copy saved on {d}. Live updates, AI features and saving work only inside Claude."});
Object.assign(T.ar,{snapNote:"نسخة للعرض فقط محفوظة بتاريخ {d}. التحديث المباشر وميزات الذكاء الاصطناعي والحفظ تعمل داخل Claude فقط."});
let SNAP_MODE=false, SNAP_AT=0, SNAP_PARTS={};
const ASSET_FILES=__ASSET_FILES__;
const assetUrl=id=>ASSET_FILES[id]||("assets/files/"+id);
/* Inside Claude files go through the platform's save dialog; elsewhere (GitHub Pages) a normal browser download. */
async function saveFile(name,data){
  if(downloads) return downloads.save({filename:name,data});
  const blob=data instanceof Blob?data:new Blob([data]); const url=URL.createObjectURL(blob);
  const a=document.createElement("a"); a.href=url; a.download=name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),4000);
  return {status:"saved"};
}
async function loadSnapshot(){
  try{
    const r=await fetch("data/snapshot.json",{cache:"no-store"}); if(!r.ok) throw new Error("snapshot "+r.status);
    const S=await r.json();
    SNAP_MODE=true; SNAP_AT=+S.exportedAt||Date.now(); SNAP_PARTS=S.weekparts||{};
    newsAll=(S.news||[]).filter(n=>n&&n.country&&n.severity); news=newsAll.filter(n=>!n.mergedInto);
    threats=S.countries||{}; briefs=S.briefs||{}; weekDocs=S.weeks||{}; reviews=S.reviews||{};
    forecasts=(S.forecasts||[]).filter(f=>f&&f.createdAt&&Array.isArray(f.scenarios)&&f.confidence&&f.dubai).sort((a,b)=>b.createdAt-a.createdAt);
    metaUpd=(S.meta&&S.meta.update)||null; isOwner=false; document.body.classList.remove("is-owner");
    status(fill(t("snapNote"),{d:fmtTs(SNAP_AT)}));
    renderAll();
  }catch(e){ console.warn(e); status(t("noDb")); renderAll(); }
}

'''


def build_page(live, asset_ids):
    g = live
    for i in set(BLOB.findall(g)):
        g = g.replace("/_blob/" + i, asset_path(i))
    # attachment paths built at run time from a stored id:  "/_blob/"+X -> assetUrl(X),  /_blob/${X} -> ${assetUrl(X)}
    g = re.sub(r'"/_blob/"\+([A-Za-z_$][\w$.]*)', r"assetUrl(\1)", g)
    g = re.sub(r"/_blob/\$\{([^}]*)\}", r"${assetUrl(\1)}", g)
    if "/_blob/" in g:
        sys.exit("build_github: unhandled /_blob/ reference left in the page")
    g = rep(g, "  const d=weekDocs[w]; if(!db||!d||!d.parts) return [];",
            "  const d=weekDocs[w]; if(!d||!d.parts) return [];\n  if(!db){ const out=[]; for(let i=0;i<d.parts;i++){ const p=SNAP_PARTS[`${w}-p${i}`]; if(p&&Array.isArray(p.items)) out.push(...p.items); } return out; }")
    g = rep(g, "const mk=()=>`morning-${todayStr()}`;",
            'const mk=()=>SNAP_MODE?(Object.keys(briefs).filter(k=>k.startsWith("morning-")).sort().pop()||`morning-${todayStr()}`):`morning-${todayStr()}`;')
    g = rep(g, "function morningItems(){ const since=Date.now()-864e5, y=addDays(todayStr(),-1);",
            "function morningItems(){ const ref=SNAP_MODE&&SNAP_AT?SNAP_AT:Date.now(), since=ref-864e5, y=addDays(todayStr(new Date(ref)),-1);")
    g = rep(g, '  if(!window.claude||!window.claude.use){ status(t("noDb")); return; }',
            "  if(!window.claude||!window.claude.use){ await loadSnapshot(); return; }")
    g = rep(g, '  if(!db){ status(t("noDb")); renderAll(); return; }', "  if(!db){ await loadSnapshot(); return; }")
    g = rep(g, '      if(!downloads) throw new Error("no-downloads");\n', "")
    g = rep(g, '      await downloads.save({filename:`${o.file}-${suffix}.${kind==="png"?"png":"pdf"}`,data});',
            '      await saveFile(`${o.file}-${suffix}.${kind==="png"?"png":"pdf"}`,data);')
    g = rep(g, '    if(!downloads){ msg(t("exportFail"),true); return; }\n', "")
    g = rep(g, "      await downloads.save({filename:fileBase(n)+ext,data});", "      await saveFile(fileBase(n)+ext,data);")
    files = {i: asset_path(i) for i in asset_ids}
    g = rep(g, "/* ---------- Render / boot ---------- */\n",
            SNAPCODE.replace("__ASSET_FILES__", json.dumps(files)) + "/* ---------- Render / boot ---------- */\n")
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True)
    ap.add_argument("--assets", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(ROOT, "platform", "index.html"), encoding="utf-8") as fh:
        live = fh.read()
    snap = snapshot(a.export)
    if not snap["news"]:
        sys.exit("build_github: export has no news — refusing to overwrite the snapshot")
    if a.assets:
        print("\n".join(needed_assets(live, snap)))
        return
    attach_ids = sorted({x["id"] for n in snap["news"] for x in (n.get("attachments") or []) if isinstance(x, dict) and x.get("id")})
    page = build_page(live, attach_ids)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    path = os.path.join(ROOT, "data", "snapshot.json")
    old = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            old = json.load(fh)
    old_at = old.pop("exportedAt", None) if old else None
    if old is not None and old == snap:
        snap = {"exportedAt": old_at, **snap}
        print("data unchanged")
    else:
        snap = {"exportedAt": int(time.time() * 1000), **snap}
        print(f"data updated: {len(snap['news'])} news, {len(snap['countries'])} countries, {len(snap['forecasts'])} forecasts")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=1)
    missing = needed_assets(live, {"news": snap["news"]})
    if missing:
        print("missing assets: " + " ".join(missing))


if __name__ == "__main__":
    main()
