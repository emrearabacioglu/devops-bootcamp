from personclass import Personclass

class Profclass(Personclass):
    
    def __init__(self, first_name, last_name, age, lectures_given):
        super().__init__(first_name, last_name, age)
        self.lectures_given = lectures_given

    def list_lectures(self):
        print(self.lectures_given)
    
    def add_lectures(self, new_lectures):
        self.lectures_given.extend(new_lectures)
        print(f"Updated lecture list: {self.lectures_given}")
        
    def leave_lectures(self, canceled_lectures):
        self.lectures_given = [lecture for lecture in self.lectures_given if lecture not in canceled_lectures]
        print(f"Updated lecture list: {self.lectures_given}")