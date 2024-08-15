import argparse
from pathlib import Path
from typing import Dict
import json

class LogFormat:
    FORMAT = format_mapping = {
        "a": "int16_t[32]",
        "b": "int8_t",
        "B": "uint8_t",
        "h": "int16_t",
        "H": "uint16_t",
        "i": "int32_t",
        "I": "uint32_t",
        "f": "float",
        "d": "double",
        "n": "char[4]",
        "N": "char[16]",
        "Z": "char[64]",
        "c": "int16_t * 100",
        "C": "uint16_t * 100",
        "e": "int32_t * 100",
        "E": "uint32_t * 100",
        "L": "int32_t latitude/longitude",
        "M": "uint8_t flight mode",
        "q": "int64_t",
        "Q": "uint64_t"
    }

    def __init__(self, type: int, length: int, name: str, format: str, column_string: str) -> None:
        self.type = int(type)
        self.length = int(length)
        self.name = str(name)
        self.columns = str(column_string).split(',')
        self.format = self.__extract_data_format(str(format), self.columns)

    def get_expected_column_count(self) -> int:
        """Get the expected number of columns

        Returns:
            int: number of columns
        """
        return len(self.columns)

    def __extract_data_format(self, format_string: str, columns: list) -> dict:
        
        format_dict = dict()
        for index, char in enumerate(format_string):
            dt_type = self.FORMAT.get(char, None)

            if dt_type is None:
                raise ValueError(f'Unknown data type in column: {char}')

            c = columns[index]
            format_dict[c] = dt_type

        return format_dict

    def __str__(self) -> str:
        return f"Name: {self.name}; Length: {self.length}; Column and Format: {self.format}"

    def __repr__(self) -> str:
        return str(self)


class OutputFile:
    """Output file object
    """

    def __init__(self, columns: list, file_name: Path, datatypes: list) -> None:
        self.columns = columns
        self.file_name = file_name
        self.datatypes = datatypes
        self.data = list()

    def add_data(self, data: list):
        self.data.append(data)
    
    def write(self):
        with open(self.file_name, 'w') as f:
            # write the header
            f.write(','.join(self.columns) + '\n')
            for d in self.data:
                f.write(','.join(d) + '\n')

        # add a json type definition file
        json_file = self.file_name.with_suffix('.json')
        print("Creating JSON datatype file: ", json_file)
        with open(json_file, 'w') as f:
            # map the columns to the datatypes
            column_datatype = dict(zip(self.columns, self.datatypes))
            f.write(json.dumps(column_datatype, indent=4))


class LogParser:
    """Parse the .log file into separate files based on the format specified in the FMT messages
    """

    def __init__(self, log_file_path: Path, output_dir: Path) -> None:
        """Initialize the LogParser object

        Args:
            log_file_path (Path): log file path
            output_dir (Path): output directory path
        """
        self.log_file_path = log_file_path
        self.output_dir = output_dir

        self.format_dict: Dict[str, LogFormat] = dict()
        self.output_csv: Dict[str, OutputFile] = dict()
    

    def parse(self):
        """Parse the log file
        """
        with open(self.log_file_path, 'r') as log_file:
            for line_no, line in enumerate(log_file):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('FMT'):
                    self.__parse_format_line(line, line_no)
                else:
                    self.__parse_data_line(line, line_no)
    
    def __split_line(self, line: str):
        return [t.strip() for t in line.split(', ')]


    def __parse_format_line(self, line: str, line_no: int):
        # FMT messages specifies the following format:
        # Type, Length, Name, Format, Columns
        # e.g.: FMT, 128, 89, FMT, BBnNZ, Type,Length,Name,Format,Columns
        # Note the columns are separated by commas with no spaces

        parts = self.__split_line(line)
        if len(parts) != 6 or not parts[0] == 'FMT':
            # this could be a mis-classified data line
            self.__parse_data_line(line, line_no)
            return
        
        dt_type = parts[1]
        dt_length = parts[2]
        dt_name = parts[3]
        dt_format = parts[4]
        dt_columns = parts[5]

        log_format = LogFormat(dt_type, dt_length, dt_name, dt_format, dt_columns)

        self.format_dict[dt_name] = log_format


    def __parse_data_line(self, line: str, line_no: int):
        parts = self.__split_line(line)
        name = parts[0]
        if name not in self.format_dict:
            print("Warning: Unknown format for line: ", line)
            return
        
        log_format = self.format_dict[name]
        expected_columns = log_format.get_expected_column_count()
        data = parts[1:]

        if len(data) != expected_columns:
            raise ValueError(f'Error on Line {line_no}. Expected {expected_columns} columns, got {len(data)}')
        

        if name not in self.output_csv:
            print(f'Creating output file for {name}')
            output_file_path = self.output_dir / Path(name).with_suffix('.csv')
            columns = log_format.columns.copy()
            datatypes = [log_format.format[c] for c in log_format.columns]            
            self.output_csv[name] = OutputFile(columns, output_file_path, datatypes)
        
        self.output_csv[name].add_data(data)
            
    def write_csv_files(self) -> None:
        """Write the output csv files
        """
        for output_file in self.output_csv.values():
            output_file.write()


def main():
    parser = argparse.ArgumentParser(description='Parse ardupilot .log file into separate files')
    parser.add_argument('log_file', type=Path, help='Path to the .log file')
    parser.add_argument('output_dir', type=Path, help='Path to the output directory')

    args = parser.parse_args()
    log_file_path: Path = args.log_file
    output_dir_path: Path = args.output_dir

    if not log_file_path.exists():
        parser.error(f'File {log_file_path} does not exist')
    
    if not log_file_path.is_file():
        parser.error(f'{log_file_path} is not a file')

    if not output_dir_path.is_dir():
        try:
            output_dir_path.mkdir(parents=True)
        except Exception as e:
            parser.error(f'Could not create output directory: {e}')
    else:
        print(f'Output directory {output_dir_path} already exists')
    
    log_parser = LogParser(log_file_path, output_dir_path)
    log_parser.parse()
    print("Parsing complete")
    log_parser.write_csv_files()
    print("CSV files written")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
        exit(0)
    except ValueError as e:
        print(f'{e.args[0]}')
        exit(1)
