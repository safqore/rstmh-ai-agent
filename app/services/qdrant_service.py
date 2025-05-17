from dotenv import load_dotenv
import os

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, '../..', '.env')
# Load the environment variables
load_dotenv(dotenv_path=env_path)