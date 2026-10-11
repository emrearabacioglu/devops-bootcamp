from userclass import Userclass
from postclass import Postclass

app_user_emre = Userclass("ee@aa.com", "Emre Arabacioglu", "pwd", "unemployed")

app_user_emre.get_user_info()
app_user_emre.change_job_title("DevOPS Engineer")
app_user_emre.get_user_info()

app_user_akif = Userclass("aa@aa.com", "Akif Arabacioglu", "pwd", "Engineer")
app_user_akif.get_user_info()

new_post = Postclass("on a secret mission today", app_user_akif.name)
new_post.get_post_info()