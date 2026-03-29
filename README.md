# 📚 Course Converter

A Python-based CLI program to fetch course info from college websites and convert it to OneCourse-formatted data.

## Features

- **Fetch course data** from a university portal via HTTP POST, supporting custom authentication cookies.
- **Convert timetable data** automatically into a standardized, portable format compatible with OneCourse.
- **Flexible CLI**: Run conversions, fetch data, and manage config with straightforward commands.
- **Customizable configuration**: Easily set web URLs, session cookies, conversion parameters, and reset configs.
- Handles both **local `.json` input files** and **direct web requests** for maximum adaptability.
- Lets you **preview** or **save** converted data, and optionally store invalid data responses for debugging.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/THGABS/course-converter.git
    cd course-converter
    ```

2. Install Python dependencies:
    ```sh
    pip install requests
    ```

## Usage

After configuration, the main script is `CourseConverter.py`. You can invoke it using Python:

```sh
python CourseConverter.py <command> [options]
```

### Subcommands

- `CourseConverter convert` - get data from web or locally and convert
- `CourseConverter fetch` - get data from web or locally
- `CourseConverter config` - show, update or reset your config

### Arguments

#### `fetch` and `convert`

- `-y`, `--year` - school year
- `-t`, `--term` - school term
- `-i`, `--input` - input file path
- `-o`, `--output` - output file path
- `-d`, `--display` - display the raw data file, instead of saving it

#### `config`

- `-u`, `--url` - school lesson URL
- `-c`, `--cookies` - cookie jar of yours (as string)
- `-i`, `--index` - max index
- `-w`, `--weeks` - max weeks
- `--reset` - reset the config
