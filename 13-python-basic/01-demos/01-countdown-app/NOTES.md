# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Write Countdown Application

### Demo Executed: Countdown App

#### Goal and Deadline Calculation
The user enters a goal and a deadline as `goal:dd.mm.yyyy`. The deadline string is converted to a `datetime` object with `strptime()`, and the remaining time is calculated from today's date.

```python
    from datetime import datetime

    user_input = input("Enter your goal with a deadline seperated by colon:\n")
    input_list = user_input.split(":")

    goal = input_list[0]
    deadline = input_list[1]

    deadline_date = datetime.strptime(deadline, "%d.%m.%Y")
    today_date = datetime.today()
    time_till = deadline_date - today_date

    hours_till = int(time_till.total_seconds() / 60 / 60)
    print(f"Time remaining for deadline: {hours_till} hours!")
```

#### Execution
Ran the script with a goal and a deadline:
```bash
    (.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/countdown.py
    Enter your goal with a deadline seperated by colon:
    complete bootcamp:05.11.2026
    Time remaining for deadline: 725 hours!
```
