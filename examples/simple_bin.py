"""Minimal example: generate a bin with ears and export STL/STEP."""
from bin_generator import make_bin, export

model = make_bin(ears=True)
export(model, "simple_bin")
