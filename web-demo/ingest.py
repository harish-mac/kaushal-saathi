"""Feed more data into the agent. Usage: python ingest.py file1.pdf file2.png ...
Sarvam Vision digitises each file to markdown and drops it into kb/ (picked up automatically)."""
import sys, os, zipfile, tempfile
import sarvam_client as sv

for path in sys.argv[1:]:
    name = os.path.splitext(os.path.basename(path))[0]
    zpath = os.path.join(tempfile.gettempdir(), name + ".zip")
    print("Digitising", path, "...")
    sv.digitise(path, zpath)
    with zipfile.ZipFile(zpath) as z:
        for m in [n for n in z.namelist() if n.endswith(".md")]:
            out = os.path.join("kb", f"{name}_{os.path.basename(m)}")
            open(out, "wb").write(z.read(m))
            print("  saved", out)
