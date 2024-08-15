# Ardupilot .LOG Splitter

Convert Ardupilot .LOG file to .CSV files (with .JSON specifying data types)

## Usage

```
usage: parser.py [-h] log_file output_dir

Parse ardupilot .log file into separate files

positional arguments:
  log_file    Path to the .log file
  output_dir  Path to the output directory

options:
  -h, --help  show this help message and exit
```

## Output Format

For each message type, a separate .csv and .json file will be generated: 
 - The CSV file will contain all the messages for the given type. The csv name will be the type of the message
 - The JSON file will contain the data type for each of the columns for the csv
