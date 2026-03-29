# Course Converter
A Python-based CLI program to fetch course info from college website, and convert it to OneCrouse-formatted data.

## Usage
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
