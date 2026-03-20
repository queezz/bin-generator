"""Minimal example: generate a bin with ears and export STL/STEP."""
from bin_generator import make_bin, export

model = make_bin(x=60,y=70,ears=False,wall=1.2)
export(model, "simple_bin")
