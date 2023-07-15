import json

def remove_duplicates(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    unique_joblinks = set()
    unique_records = []
    removed_records = []

    for job in data:
        joblink = job['JobLink']
        if joblink not in unique_joblinks:
            unique_joblinks.add(joblink)
            unique_records.append(job)
        else:
            removed_records.append(job)

    with open(output_file, 'w') as file:
        json.dump(unique_records, file, indent=4)

    with open("removed_duplicate_records.json", 'w') as removed_file:
        json.dump(removed_records, removed_file, indent=4)

    print("Removed Duplicate Records:")
    for removed_record in removed_records:
        print(removed_record)

# Provide the paths to the input and output files
input_file = 'masterdatabase.json'
output_file = 'UniqueJobsdataMasterFile.json'

remove_duplicates(input_file, output_file)
