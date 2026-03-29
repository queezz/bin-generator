"""Minimal example: generate a bin with ears and export STL/STEP."""
from bin_generator import make_bin, export

model = make_bin(x=100,y=200,h=60,ears=False,wall=1.8,pattern=True)
export(model, "simple_bin")
