import os
import datetime
from datetime import timezone

def log_interaction(user_id, session_id, query, response, source):
    with open("interactions.log", "a") as log_file:
        log_file.write(f"{datetime.datetime.now(timezone.utc)} - User: {user_id}, Session: {session_id}, Query: {query}, Response: {response}, Source: {source}\n")