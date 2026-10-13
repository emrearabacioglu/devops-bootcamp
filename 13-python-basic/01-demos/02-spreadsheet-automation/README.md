# Automation with Python

**Technologies:** Python, VS Code, Git

A Python script that reads an inventory spreadsheet with `openpyxl`, prints some numbers per supplier and saves a new spreadsheet with an extra column.

## Summary
- `xlsxautomation.py` opens `inventory.xlsx` (columns: Product No, Inventory, Price, Supplier) and goes through every row once.
- It counts the products per supplier.
- It calculates the total inventory value (inventory × price) per supplier.
- It lists the products with less than 10 items in stock (product no: count).
- It writes the inventory value of each product into column 5 and saves the result as a new file, `inventory_with_total_value.xlsx`.

## Run
The script reads `inventory.xlsx` from the same folder. `inventory_with_total_value.xlsx` in this folder is the output of this run.
```bash
pip install openpyxl
python xlsxautomation.py
```

## Result
Product count per supplier, total value per supplier and products under 10 in stock:
```
(.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/xlsxautomation.py
adding a new supplier
adding a new supplier
adding a new supplier
{'AAA Company': 43, 'BBB Company': 17, 'CCC Company': 14}
{'AAA Company': 10969059.95, 'BBB Company': 2375499.47, 'CCC Company': 8114363.62}
{25: 7, 30: 6, 74: 2}
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
