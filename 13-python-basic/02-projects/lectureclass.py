class Lectureclass:
    
    def __init__(self, name, quota, duration, prof_list):
        self.name = name
        self.quota = quota
        self.duration = duration
        self.prof_list = prof_list
    
    def print_info(self):
        print(f"Name of lecture: {self.name}\nDuration: {self.duration}")
        
    def add_prof(self, prof_toadd):
        self.prof_list.extend(prof_toadd)
        print(f"Updated list of professors: {self.prof_list}")
        
