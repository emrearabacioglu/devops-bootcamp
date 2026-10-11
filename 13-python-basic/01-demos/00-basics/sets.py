my_set = {"Jan", "Feb", "Mar"}
for element in my_set:
    print(element)
    
my_set.add("Apr")
print(my_set)

my_set.remove("Jan")
print(my_set)

my_list = ["Jan", "Feb", "Mar", "Jan"]
my_list.remove("Jan")
print(my_list)