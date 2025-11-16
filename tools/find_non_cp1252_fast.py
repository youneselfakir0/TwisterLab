import os

roots = [r"c:\\TwisterLab\\agents", r"c:\\TwisterLab\\api", r"c:\\TwisterLab\\tests"]
errors = []
for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".py"):
                p = os.path.join(dirpath, fname)
                try:
                    with open(p, "r", encoding="cp1252") as f:
                        f.read()
                except Exception as e:
                    errors.append((p, repr(e)))

for path, err in errors:
    print(path)
    print(err)

print(f"Found {len(errors)} files with cp1252 decode issues")
