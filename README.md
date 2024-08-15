# Ardupilot .log to .csv

Convert Ardupilot .log file to .csv files (with .json specifying data types)

To generate a .log file, use [Mission Planner](https://github.com/ArduPilot/MissionPlanner) to download the .bin log of the drone. After that, use `Convert .bin to .log` function (Same place as downloading .bin log) to obtain a .log file.

The .log file is meant to present the data in a more human readable format. However, since I need to process a specific message type and the lack of existing tools, I've created this command line tool to help with such process.

## Requirements

This script is tested against Python 3.11. However, lower version (up to Python 3.8) should work without issue.

All libraries used are from Python's standard library so no extra installations are required.

This script is tested working on Linux (Ubuntu 22.04), however it should work on Windows and MacOS as well (As there are no Linux specific dependencies)

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

Example:

`$ python3 parser.py ./00000026.log ./output/`
## Output Format

For each message type, a separate .csv and .json file will be generated: 
 - The CSV file will contain all the messages for the given type. The csv name will be the type of the message
 - The JSON file will contain the data type for each of the columns for the csv
