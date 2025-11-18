#SMART_HABIT_PROGRAM

#Create Claas 
class SmartHabit:
    def __init__(self):
        self.habits=[] #create an empty list to store habits
        self.next_id=1 #habit ID counter
    def add_habit(self):
        print("Add a new habit")
        name =input("Enter habit name: ")

        while True: #loop until valid target is entered
           target =input("Enter habit target as hours per a day: ")
           if target.strip()=="":
            print("Target can not be empty")
           else:
               try:
                    target=float(target)
                    break
               except:
                   print("Invalid,Please enter a valid numeric value. ")

        #create habit dictionary
        habit={
               "id": self.next_id,
               "name":name,
               "target_hours":target,
               "today_hours":0.0,
               "completed":False
         }
        self.habits.append(habit)   #add habit to the list
        print(f"Habit {name} added with ID {self.next_id}")
        self.next_id+=1    #increment ID counter

    def find_habit_by_id(self,habit_id):
        #find habit in the list by ID
        for habit in self.habits:
            if habit['id']==habit_id:
                return habit
        return None 

    def mark_habit_completed(self):
            print("Mark habit as completed")

            if not self.habits:
                print("No habits yet")
                return

            for habit in self.habits:
                print(f"{habit['id']} {habit['name']} (target {habit['target_hours']}h)")
            #get user choice by ID
            try: 
                choice=int(input("choose habit ID: "))
                habit = self.find_habit_by_id(choice)
                if habit is None:
                    print("Invalid habit ID")
                    return

            except:
                print("Invalid input.")
                return

            # get today's hours
            hours= float(input("How many hours did you do today?"))
            habit["today_hours"] +=hours
            habit["completed"] = habit["today_hours"] >= habit["target_hours"]

            if habit["completed"]:
                print("Great job,you have complated your habit for today. ")
            else:
                print("Not completed yet.")

    def show_habits(self):
        print("All Habits")
        if not self.habits:
            print("No habits to show. ")
            return

        # print each habit
        for habit in self.habits:
            print(f"Habit ID {habit['id']}:")
            for key, value in habit.items(): # show key and value
                print(f"{key}:{value}")

    def delete_habit(self):
        print("Delete Habit")

        if not self.habits:
            print("No habits to delete.")
            return

        #show habit list
        for habit in self.habits:
            print(f"{habit['id']} {habit['name']}.")
       
        #choose habit ID to delete
        try:
             choice=int(input("Choose habit ID to delete: "))
             habit=self.find_habit_by_id(choice)
             if habit is None:
               print("Invalid ID. ")
               return

             self.habits.remove(habit)
             print(f"habit {habit['name']} deleted.")

        except:
             print("Invalid input.")

    def run(self):
         while True:
             #menu options
             print("Smart Habit")
             print("1) Add habit")
             print("2) Mark habit as completed")
             print("3) Show all habits")
             print("4) Delete habit")
             print("5) Exit")

             choice = input("Choose: ")
             if choice=="1":
                 self.add_habit()
             elif choice=="2":
                  self.mark_habit_completed()
             elif choice=="3":
                 self.show_habits()
             elif choice=="4":
                 self.delete_habit()
             elif choice=="5":
                 print("Goodbye.")
                 break
             else:
                 print("Invalid option.")
#start program
traker=SmartHabit()
traker.run()
