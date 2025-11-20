#  SMART HABIT PROGRAM

A simple Python-based console application designed to help you build and track your daily habits using hourly goals.  
You can add habits, log daily progress, track completion percentage, and receive motivational messages based on your performance. 

---

##  What Is Smart Habit?

Smart Habit is a CLI (Command Line Interface) habit tracker that allows you to:

- Add new habits with **daily hour targets**
- Log how many hours you completed today
- See your **progress percentage**
- Check whether you:
  - Haven’t reached the target yet
  - Completed the target
  - Exceeded (overachieved) the target 
- View all habits
- Delete habits you no longer need

Everything is stored in memory using a list of Python dictionaries.

---

##  Features

- ➕ Add habits with a target number of hours per day  
- 🕒 Log progress for each habit  
- 🔥 Overachievement detection with motivational messages  
- 📊 Progress percentage calculation  
- 👀 View all habits in a clean format  
- 🗑️ Delete habits using their number  
- 📟 User-friendly text menu system

---

## Habit Structure

Each habit is stored as a Python dictionary:

```python
{
   "number": 1,
   "name": "Reading",
   "target_hours": 2.0,
   "today_hours": 0.0,
   "completed": False
}
```
## How the Program Works

The program provides several key functions:

1️⃣ Add Habit

Enter habit name

Enter daily target hours

Habit is saved in the tracker

2️⃣ Mark Habit as Completed

Select a habit by number

Enter hours completed today

Program calculates:

Updated total hours

Completion percentage

Completion status:

Below target: “Keep going”

Reached target: “Great job!”

Exceeded target: “Outstanding work!”

3️⃣ Show All Habits

Displays:

Habit number

Name

Target hours

Today's hours

Completion flag

Progress percentage

4️⃣ Delete Habit

Remove a habit by selecting its number.

5️⃣ Exit

Close the program.
## Work Team 
1- Bader Aljubayri

2- Ghala Almutairi

3- Joud alkhaldy 

4- Ali Arishi

5- Abeer Alharbi
