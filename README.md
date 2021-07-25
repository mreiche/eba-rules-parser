# Eba rules parser

## Goal

Parse formulars from the validation file.

```
{r0020} = {r0030} + {r0130} + {r0180} + {r0200} + {r0210} + {r0220} + {r0230} + {r0240} + {r0250} + {r0300} + {r0340} + {r0370} + {r0380} + {r0390} + {r0430} + {r0440} + {r0450} + {r0460} + {r0470} + {r0471} + {r0472} + {r0480} + {r0490} + {r0500} + {r0510} + {r0513} + {r0514} + {r0515} + {r0520} + {r0524} + {r0529}
```

And eval them like:
```python
ret = eval("30 == 13.3 + 52 + ...")
```

## Files

- `test.py`: Contains tests for parsing and evaluating rules using custom test report.
- `report.py`: Runs rules from official validation file against sheet mappers.
