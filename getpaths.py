# FILE USED TO EXTRACT ALL VALID PUZZLES FROM nyt_crosswords github repo

import os
import csv

def save_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Month', 'Day'])
        writer.writerows(data)

def get_date_combinations(folder_path):
    date_combinations = []
    for year_folder in os.listdir(folder_path):
        year_path = os.path.join(folder_path, year_folder)
        if os.path.isdir(year_path):
            for month_folder in os.listdir(year_path):
                month_path = os.path.join(year_path, month_folder)
                if os.path.isdir(month_path):
                    for day_file in os.listdir(month_path):
                        if day_file.endswith('.json'):
                            day = day_file.split('.')[0]
                            date_combinations.append((year_folder, month_folder, day))
    return date_combinations

# Example usage
folder_path = 'nyt_crosswords'  # Replace 'folder' with the actual path to your directory
date_combinations = get_date_combinations(folder_path)
save_to_csv(date_combinations, 'date_combinations.csv')