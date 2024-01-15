import datetime

file_name = "dddd-2024-01-15_11-17-38"
suffix = "%Y-%m-%d_%H-%M-%S"
    
import re

pattern = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")

if pattern.search(file_name):
    print("yes")