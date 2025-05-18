```
Note: Run all python commands in this (technical-analysis/) directory only
```

Activate poetry environment
On Linux: `eval $(poetry env activate)`

run 
`alias rm-pycache-in-current-dir='find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf'`

and 
`rm-pycache-in-current-dir`

to remove `__pycache__/`