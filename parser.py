import argparse
from pathlib import Path


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

    def __init__(self, length: int, name: str, format: str, column_string: str) -> None:
        self.length = length
        self.name = name
        self.columns = column_string.split(',')
        self.format = self.__extract_data_format(format, self.columns)

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

class LogParser:
    def __init__(self, log_file_path: Path, output_dir: Path) -> None:
        self.log_file_path = log_file_path
        self.output_dir = output_dir

        self.format_dict = dict()
    
    def parse(self):
        with open(self.log_file_path, 'r') as log_file:
            for line in log_file:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('FMT'):
                    self.__parse_format_line(line)
                else:
                    self.__parse_data_line(line)
    
    def __parse_format_line(self, line: str):
        # FMT messages specifies the following format:
        # Type, Length, Name, Format, Columns
        # e.g.: FMT, 128, 89, FMT, BBnNZ, Type,Length,Name,Format,Columns
        # Note the columns are separated by commas with no spaces

        parts = [t.strip() for t in line.split(', ')]
        if len(parts) != 6 or not parts[0] == 'FMT':
            # this could be a mis-classified data line
            self.__parse_data_line(line)
            return
        
        dt_type = parts[1]
        dt_length = parts[2]
        dt_name = parts[3]
        dt_format = parts[4]
        dt_columns = parts[5]

        log_format = LogFormat(dt_length, dt_name, dt_format, dt_columns)

        self.format_dict[dt_type] = log_format
        print(self.format_dict)


    def __parse_data_line(self, line: str):
        pass
            

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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
        exit(0)
