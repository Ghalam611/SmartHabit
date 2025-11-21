# SMART_HABIT_PROGRAM

import json
from datetime import datetime, timedelta

# Create Class 
class SmartHabit:
    def __init__(self):
        self.habits = []  # create an empty list to store habits
        self.next_number = 1  # habit counter
        self.data_file = "habits_data.json"
        self.load_data()
    
    def load_data(self):
        #Load data from JSON file
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.habits = data.get('habits', [])
                self.next_number = data.get('next_number', 1)
                
                # Add missing fields for backward compatibility
                for habit in self.habits:
                    if 'created_date' not in habit:
                        habit['created_date'] = datetime.now().strftime("%Y-%m-%d")
                    if 'daily_progress' not in habit:
                        habit['daily_progress'] = {}
                    # Initialize today's tracking for all habits
                    self.initialize_daily_tracking(habit)
                print("Data loaded successfully!")
                        
        except FileNotFoundError:
            print("No data file found, starting fresh.")
            self.habits = []
            self.next_number = 1
    
    def save_data(self):
        #Save data to JSON file
        data = {
            'habits': self.habits,
            'next_number': self.next_number,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("Data saved successfully!")
    
    def initialize_daily_tracking(self, habit):
        #Initialize daily tracking for habit
        today = datetime.now().strftime("%Y-%m-%d")
        
        if 'daily_progress' not in habit:
            habit['daily_progress'] = {}
        
        # Initialize today with 0 hours if not exists
        if today not in habit['daily_progress']:
            habit['daily_progress'][today] = 0
    
    def calculate_daily_score(self):
        #Calculate today's total score for all habits using lambda functions
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Lambda function to calculate completion ratio for a single habit
        calculate_habit_score = lambda habit: (
            min(habit['daily_progress'].get(today, 0) / habit['target_hours'], 1.0) * 100 
            if habit['target_hours'] > 0 else 0
        )
        
        # Lambda function to check if habit is completed today
        is_habit_completed = lambda habit: (
            habit['daily_progress'].get(today, 0) >= habit['target_hours']
        )
        
        # Calculate scores using map and lambda
        habit_scores = list(map(calculate_habit_score, self.habits))
        
        # Count completed habits using filter and lambda
        completed_habits = len(list(filter(is_habit_completed, self.habits)))
        
        # Calculate averages using lambda and reduce
        if self.habits:
            daily_score = (lambda scores: sum(scores) / len(scores))(habit_scores)
        else:
            daily_score = 0
            
        return {
            'date': today,
            'daily_score': round(daily_score, 1),
            'completed_habits': completed_habits,
            'total_habits': len(self.habits),
            'completion_percentage': round((completed_habits / len(self.habits) * 100) if self.habits else 0, 1),
            'habit_scores': habit_scores
        }
    
    def get_weekly_progress(self, habit_number):
        #Get weekly progress for a specific habit using lambda functions
        habit = self.find_habit_by_number(habit_number)
        if not habit:
            return None
        
        # Ensure daily_progress exists
        if 'daily_progress' not in habit:
            habit['daily_progress'] = {}
        
        # Lambda function to calculate daily progress data
        calculate_daily_data = lambda days_ago: (
            lambda date: {
                'date': date,
                'hours': habit['daily_progress'].get(date, 0),
                'target': habit['target_hours'],
                'completed': habit['daily_progress'].get(date, 0) >= habit['target_hours'],
                'completion_percentage': min(
                    (habit['daily_progress'].get(date, 0) / habit['target_hours'] * 100) 
                    if habit['target_hours'] > 0 else 0, 
                    100
                )
            }
        )((datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d"))
        
        # Generate weekly data using map and lambda
        weekly_data = list(map(calculate_daily_data, range(7)))
        
        return weekly_data
    
    def habit_exists(self, name):
        #check if a habit with the same name already exists
        normalized = name.strip().lower()
        return any(habit['name'].strip().lower()== normalized for habit in self.habits)

    def add_habit(self):
        print(":" * 20)
        print("Add a new habit")

        while True:
            name = input("Enter habit name: ")
            if name =="":
                print("Habit name can not be empty. ")
                continue
            if self.habit_exists(name):
                print("This habit already exisit. please enter a different habit. ")
                continue
            break

        while True:
            target = input("Enter habit target as hours per a day: ")
            if target.strip() == "":
                print("Target can not be empty")
                print(":" * 20)
                continue
            try:
                target = float(target)
                print(":" * 20)
                break
            except:
                print("Invalid, Please enter a valid numeric value. ")
                print(":" * 20)

        # create habit dictionary with daily tracking
        habit = {
            "number": self.next_number,
            "name": name,
            "target_hours": target,
            "today_hours": 0,
            "completed": False,
            "daily_progress": {},
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Initialize today's tracking
        self.initialize_daily_tracking(habit)
        
        self.habits.append(habit)
        print(f"Habit '{name}' added with number {self.next_number}")
        self.next_number += 1
        self.save_data()

    def find_habit_by_number(self, habit_number):
        # Lambda function to find habit by number
        found_habits = list(filter(lambda habit: habit['number'] == habit_number, self.habits))
        return found_habits[0] if found_habits else None

    def mark_habit_completed(self):
        print(":" * 20)
        print("Mark habit as completed")

        if not self.habits:
            print("No habits yet")
            print(":" * 20)
            return

        for habit in self.habits:
            print(f"{habit['number']} - {habit['name']} (target {habit['target_hours']}h)")
        
        try:
            choice = int(input("Choose habit Number: "))
            habit = self.find_habit_by_number(choice)
            if habit is None:
                print("Invalid habit Number")
                print(":" * 20)
                return
        except:
            print("Invalid input.")
            print(":" * 20)
            return

        # Initialize daily tracking
        self.initialize_daily_tracking(habit)
        
        # get today's hours
        while True:
            hours = input("How many hours did you do today? ")
            if hours.strip() == "":
                print("Hours can not be empty. ")
                continue
            try:
                hours = float(hours)
                break
            except:
                print("Invalid input. Enter a numeric value.")

        # Update today's progress
        today = datetime.now().strftime("%Y-%m-%d")
        habit["today_hours"] = hours
        habit["daily_progress"][today] = hours
        habit["completed"] = habit["today_hours"] >= habit["target_hours"]
        
        total_percentage = (habit["today_hours"] / habit["target_hours"]) * 100
        
        if habit["target_hours"] == habit["today_hours"]:
            print("Great job, you have completed your habit for today.")
        elif habit["today_hours"] > habit["target_hours"]:
            print("Outstanding work! You didn't just reach your goal - you went beyond it!")
        else:
            print("Not completed yet. Keep going!")
        
        print(f"Your total hours: {habit['today_hours']}h / Target: {habit['target_hours']}h")
        print(f"Your progress: {round(total_percentage, 1)}%")
        
        # Show daily score
        daily_score = self.calculate_daily_score()
        print(f"Today's Score: {daily_score['daily_score']}%")
        print(f"Completed: {daily_score['completed_habits']}/{daily_score['total_habits']} habits")
        
        print(":" * 20)
        self.save_data()

    def show_habits(self):
        print(":" * 20)
        print("All Habits")
        if not self.habits:
            print("No habits to show.")
            print(":" * 20)
            return

        for habit in self.habits:
            print(f"\nHabit Number {habit['number']}:")
            print(f"  Name: {habit['name']}")
            print(f"  Target: {habit['target_hours']} hours per day")
            print(f"  Created: {habit.get('created_date', 'Unknown')}")
            
            # Show today's progress
            today = datetime.now().strftime("%Y-%m-%d")
            today_hours = habit['daily_progress'].get(today, 0)
            print(f"  Today's hours: {today_hours}h")
            
            if habit["target_hours"] > 0:
                total_percentage = (today_hours / habit["target_hours"]) * 100
                print(f"  Today's progress: {round(total_percentage, 1)}%")
            else:
                print("  Today's progress: 0%")
            
            if today_hours >= habit['target_hours']:
                print("  Status: ✅ Completed")
            else:
                print("  Status: ⏳ In Progress")
        
        print(":" * 20)

    def show_daily_score(self):
        #Show today's score and progress report
        print(":" * 20)
        print("Today's Progress Report")
        
        daily_score = self.calculate_daily_score()
        print(f"Date: {daily_score['date']}")
        print(f"Overall Score: {daily_score['daily_score']}%")
        print(f"Completed Habits: {daily_score['completed_habits']}/{daily_score['total_habits']}")
        print(f"Completion Rate: {daily_score['completion_percentage']}%")
        
        print("\nHabit Details:")
        for habit in self.habits:
            today = datetime.now().strftime("%Y-%m-%d")
            today_hours = habit['daily_progress'].get(today, 0)
            target = habit['target_hours']
            status = "✅" if today_hours >= target else "⏳"
            percentage = min((today_hours / target * 100) if target > 0 else 0, 100)
            
            print(f"  {status} {habit['name']}: {today_hours}h / {target}h ({round(percentage, 1)}%)")
        
        print(":" * 20)

    def show_weekly_progress(self):
        """Show weekly progress for a habit"""
        print(":" * 20)
        print("Weekly Progress")
        
        if not self.habits:
            print("No habits to show.")
            print(":" * 20)
            return
        
        for habit in self.habits:
            print(f"{habit['number']} - {habit['name']}")
        
        try:
            choice = int(input("Choose habit number to view weekly progress: "))
            weekly_data = self.get_weekly_progress(choice)
            
            if weekly_data:
                habit = self.find_habit_by_number(choice)
                print(f"\nWeekly progress for {habit['name']}:")
                print("-" * 50)
                for day in weekly_data:
                    status = "✅" if day['completed'] else "❌"
                    print(f"  {day['date']}: {status} {day['hours']}h / {day['target']}h ({round(day['completion_percentage'], 1)}%)")
                
                # Weekly statistics
                completed_days = sum(1 for day in weekly_data if day['completed'])
                total_hours = sum(day['hours'] for day in weekly_data)
                average_hours = total_hours / len(weekly_data)
                
                print("-" * 50)
                print(f"Weekly Summary:")
                print(f"  Completed Days: {completed_days}/7")
                print(f"  Total Hours: {total_hours:.1f}h")
                print(f"  Daily Average: {average_hours:.1f}h")
            else:
                print("Invalid habit number.")
        except:
            print("Invalid input.")
        
        print(":" * 20)

    def delete_habit(self):
        print(":" * 20)
        print("Delete Habit")

        if not self.habits:
            print("No habits to delete.")
            print(":" * 20)
            return

        for habit in self.habits:
            print(f"{habit['number']} - {habit['name']}")

        try:
            choice = int(input("Choose habit number to delete: "))
            habit = self.find_habit_by_number(choice)
            if habit is None:
                print("Invalid number.")
                return

            # Confirmation
            confirm = input(f"Are you sure you want to delete '{habit['name']}'? (yes/no): ")
            if confirm.lower() in ['yes', 'y']:
                self.habits.remove(habit)
                print(f"Habit '{habit['name']}' deleted.")
                self.save_data()
            else:
                print("Deletion cancelled.")
            
            print(":" * 20)
        except:
            print("Invalid input.")
            print(":" * 20)

    def run(self):
        while True:
            print("=" * 50)
            print("            SMART HABIT TRACKER")
            print("=" * 50)
            print("1) Add habit")
            print("2) Mark habit as completed")
            print("3) Show all habits")
            print("4) Delete habit")
            print("5) Show today's score")
            print("6) Show weekly progress")
            print("7) Exit")
            print("=" * 50)

            choice = input("Choose an option (1-7): ")
            
            if choice == "1":
                self.add_habit()
            elif choice == "2":
                self.mark_habit_completed()
            elif choice == "3":
                self.show_habits()
            elif choice == "4":
                self.delete_habit()
            elif choice == "5":
                self.show_daily_score()
            elif choice == "6":
                self.show_weekly_progress()
            elif choice == "7":
                print("Goodbye! Keep building good habits! 👋")
                break
            else:
                print("Invalid option. Please choose 1-7.")

# Start program
if __name__ == "__main__":
    tracker = SmartHabit()
    tracker.run()