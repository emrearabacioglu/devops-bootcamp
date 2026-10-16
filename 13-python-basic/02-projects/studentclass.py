from personclass import Personclass

class Studentclass(Personclass):
    
    def __init__(self, first_name, last_name, age, lectures_attend):
        super().__init__(first_name, last_name, age)
        self.lectures_attend = lectures_attend
    
    def list_lectures(self):
        print(self.lectures_attend)
        
    def add_lectures(self, new_lectures):
        self.lectures_attend.extend(new_lectures)
        print(f"Updated lecture list: {self.lectures_attend}")
        
    def leave_lectures(self, dropped_lectures):
        self.lectures_attend = [lecture for lecture in self.lectures_attend if lecture not in dropped_lectures]
        print(f"Updated lecture list: {self.lectures_attend}")