# Show IAM users and their last activity
# Get all the IAM users in your AWS account
# For each user, print out the name of the user and when they were last active
# Print out the user ID and name of the user who was active the most recently

import boto3
from datetime import datetime, timezone

client = boto3.client("iam", region_name="eu-central-1")

response = client.list_users()
now = datetime.now(timezone.utc)
userlist = []
for user in response["Users"]: 
    iamuser = user["UserName"]
    userid = user["UserId"]
    last_active = user["PasswordLastUsed"]
    diff = (now - last_active).days
    print(f"User: {iamuser} Last active: {last_active}, {diff} days ago")
    dictionary = {
        "username":iamuser,
        "user_id":userid,
        "last_active_days":diff
    }
    userlist.append(dictionary)
    
userlist_sorted = sorted(userlist, key=lambda days: days["last_active_days"])
print(f"Most recent user: {userlist_sorted[0]["username"]}\nUser ID: {userlist_sorted[0]["user_id"]}")