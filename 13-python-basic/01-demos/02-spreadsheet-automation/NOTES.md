# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Automation with Python

### Demo Executed: Spreadsheet Automation with openpyxl

#### Inventory Processing
The script reads `inventory.xlsx` (columns: Product No, Inventory, Price, Supplier), goes through every row once and:

* counts products per supplier,
* calculates the total inventory value per supplier,
* lists products with less than 10 items in stock,
* writes the inventory value of each product into column 5 and saves the result as a new file (`inventory_with_total_value.xlsx`).

`xlsxautomation.py`:
```python
    import openpyxl

    inv_file = openpyxl.load_workbook("inventory.xlsx")
    product_list = inv_file["Sheet1"]

    products_per_supplier = {}
    total_value_per_supplier = {}
    products_under_10_inv = {}

    for product_row in range(2, product_list.max_row + 1):
        supplier_name = product_list.cell(product_row, 4).value
        inventory = product_list.cell(product_row, 2).value
        price = product_list.cell(product_row, 3).value
        product_num = product_list.cell(product_row, 1).value
        inventory_price = product_list.cell(product_row, 5)

        # product count per supplier
        if supplier_name in products_per_supplier:
            current_num_products = products_per_supplier.get(supplier_name)
            products_per_supplier[supplier_name] = current_num_products +1
        else:
            print("adding a new supplier")
            products_per_supplier[supplier_name] = 1

        # total inventory value per supplier
        if supplier_name in total_value_per_supplier:
            current_total_value = total_value_per_supplier.get(supplier_name)
            total_value_per_supplier[supplier_name] = current_total_value + inventory * price
        else :
            total_value_per_supplier[supplier_name] = inventory * price

        # products under 10 in inventory
        if inventory < 10 :
            products_under_10_inv[int(product_num)] = int(inventory)

        # add value for total inventory price
        inventory_price.value = inventory * price

    print(products_per_supplier)
    print(total_value_per_supplier)
    print(products_under_10_inv)

    inv_file.save("inventory_with_total_value.xlsx")
```

#### Execution
Output: product count per supplier, total value per supplier, and products under 10 in stock (product no: count):
```bash
    (.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/xlsxautomation.py
    adding a new supplier
    adding a new supplier
    adding a new supplier
    {'AAA Company': 43, 'BBB Company': 17, 'CCC Company': 14}
    {'AAA Company': 10969059.95, 'BBB Company': 2375499.47, 'CCC Company': 8114363.62}
    {25: 7, 30: 6, 74: 2}
```
