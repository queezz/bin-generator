# Simple bin

## CLI howto

### Install (editable)

```bash
python -m pip install -e .
```

### Generate a bin

```bash
bin-gen --help
bin-gen --ears -o my_bin
```

- `-o/--output`: output path stem (by default creates `<stem>-<x>-<y>-<h>.stl` and/or `.step`)
- `--suppress-default-suffix`: do not append `-<x>-<y>-<h>` to the filename
- `--x --y --h`: dimensions
- `--wall`: wall thickness

## Venv
**Windows PowerShell:**

```powershell
python -m venv "$env:USERPROFILE/.venvs/cad"
```

### Activate virtual environment

**Linux / macOS:**

```bash
source ~/.venvs/cad/bin/activate
```

**Windows PowerShell:**

```powershell
& "$env:USERPROFILE/.venvs/cad/Scripts/Activate.ps1"
```