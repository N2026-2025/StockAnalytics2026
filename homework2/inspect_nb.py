import nbformat

for p in ["homework2/Homework02.ipynb", "homework2/H02.ipynb"]:
    try:
        nb = nbformat.read(p, as_version=4)
    except Exception as e:
        print(f"{p}: READ ERROR: {e}")
        continue
    cells = [c for c in nb.cells if c.cell_type == "code"]
    errs = [o.get("ename") for c in cells for o in c.outputs if o.output_type == "error"]
    src = "".join(c.source for c in cells)
    print(f"--- {p} ---")
    print(f"  cells total={len(nb.cells)}, code={len(cells)}")
    print(f"  errors={errs}")
    print(f"  all_have_outputs={all(bool(c.outputs) for c in cells)}")
    print(f"  dynamic_q3={'for m in (1, 3, 6, 12)' in src}")
    print(f"  kernel={nb.metadata.get('kernelspec', {}).get('name')}")
    print(f"  mentions_q5={'Post-Earnings Gate' in src}")
