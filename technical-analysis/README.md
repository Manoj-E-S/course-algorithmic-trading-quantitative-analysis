`Note: Run all python commands in this (technical-analysis/) directory only`

Activate poetry environment
1. On Linux: 
```
eval $(poetry env activate)
```

To remove all `__pycache__/` directories created after a python script is run:
```
poetry run poe rm-pycache
```