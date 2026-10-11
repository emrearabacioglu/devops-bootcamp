# Write Countdown Application

**Technologies:** Python, VS Code, Git

A small Python app that asks for a goal and a deadline and prints how many hours are left until the deadline.

## Summary
- `countdown.py` reads the user input in the format `goal:dd.mm.yyyy` and splits it at the colon into goal and deadline.
- The deadline string is converted to a date with `datetime.strptime()`.
- Today's date is subtracted from the deadline and the difference is converted to hours.

## Run
```bash
python countdown.py
```

## Result
Goal `complete bootcamp` with deadline `05.11.2026`, and the hours left:
```
(.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/countdown.py
Enter your goal with a deadline seperated by colon:
complete bootcamp:05.11.2026
Time remaining for deadline: 725 hours!
```

Full step-by-step notes with terminal output: [NOTES.md](./NOTES.md)
