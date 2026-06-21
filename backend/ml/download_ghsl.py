"""Download GHSL GHS_BUILT_S epoch tiles for ChronoCity cities."""
import urllib.request, pathlib, zipfile, os, sys, time

OUT = pathlib.Path(r"D:\PROJELER\ghsl_raw")
OUT.mkdir(parents=True, exist_ok=True)

BASE = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A"

EPOCHS = ["E1975", "E1990", "E2000", "E2010", "E2020"]

# Tiles covering our 11 cities (computed via Mollweide projection)
# new-york=R5_C12, chicago=R5_C11, berlin=R3_C20, vienna=R4_C20,
# paris=R4_C19, london=R3_C19, barcelona=R5_C19, madrid=R5_C18,
# moscow=R3_C21, istanbul=R5_C21, tokyo=R5_C31
TILES = ["R3_C19", "R3_C20", "R3_C21", "R4_C19", "R4_C20",
         "R5_C11", "R5_C12", "R5_C18", "R5_C19", "R5_C21", "R5_C31"]

def progress(count, block, total):
    pct = min(count * block * 100 // total, 100)
    bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
    print(f"\r  [{bar}] {pct}%  ", end="", flush=True)

total_files = len(EPOCHS) * len(TILES)
done = 0
skipped = 0
failed = []

for epoch in EPOCHS:
    epoch_dir = OUT / epoch
    epoch_dir.mkdir(exist_ok=True)
    for tile in TILES:
        name = f"GHS_BUILT_S_{epoch}_GLOBE_R2023A_54009_100_V1_0_{tile}"
        zip_path = epoch_dir / f"{name}.zip"
        tif_path = epoch_dir / f"{name}.tif"

        if tif_path.exists():
            skipped += 1
            done += 1
            print(f"SKIP {epoch}/{tile} (already extracted)")
            continue

        url = f"{BASE}/GHS_BUILT_S_{epoch}_GLOBE_R2023A_54009_100/V1-0/tiles/{name}.zip"
        print(f"[{done+1}/{total_files}] {epoch}/{tile} ...", end=" ")

        try:
            urllib.request.urlretrieve(url, zip_path, reporthook=progress)
            print()
            # Extract .tif
            with zipfile.ZipFile(zip_path) as z:
                tifs = [n for n in z.namelist() if n.endswith(".tif")]
                if tifs:
                    z.extract(tifs[0], epoch_dir)
                    extracted = epoch_dir / tifs[0]
                    if str(extracted) != str(tif_path):
                        extracted.rename(tif_path)
            zip_path.unlink()
            size_mb = tif_path.stat().st_size // 1_048_576
            print(f"  OK → {tif_path.name} ({size_mb} MB)")
        except Exception as e:
            print(f"\n  FAILED: {e}")
            failed.append(f"{epoch}/{tile}")
            if zip_path.exists():
                zip_path.unlink()

        done += 1

print(f"\nDone. Skipped={skipped}, Failed={len(failed)}")
if failed:
    print("Failed tiles:", failed)
print(f"Output: {OUT}")
