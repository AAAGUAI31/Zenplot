# Validate Draw.io XML Tool Contract

This is a mechanical validation step.

## Input

- draw.io XML file

## Output

- validation status
- parse errors if any

## Requirements

- Check XML well-formedness.
- Check that `<mxfile>` and at least one `<diagram>` exist.
- Do not modify the XML.
- Do not infer layout quality; that belongs to Visual QA.
