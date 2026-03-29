import json

CONFIG_FILE = 'CourseConverter.json'
config = {
  'WebFetcher': {
    'url': 'http://xsjw2018.jw.scut.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N2151',
    'cookies': {}
  },
  'FormatConverter': {
    'max_idx': 11,
    'max_weeks': 20
  }
}
YES_TUPLE = ('y', 'Y', 'Yes', 'yes', 'YES')

def show_configs():
  global config
  print(json.dumps(config, indent=2))
  print()

def save_config(data:object=config['FormatConverter'], section:str='FormatConverter'):
  global config, CONFIG_FILE
  config[section] = data
  save_json(config, CONFIG_FILE)

def save_configs(data:object=config):
  global config, CONFIG_FILE
  config = data
  save_json(config, CONFIG_FILE, indent=2)
  print('Configs have been successfully updated.')

def read_configs():
  global config, CONFIG_FILE
  config_candidate = load_json(CONFIG_FILE)
  if config_candidate and isinstance(config_candidate, dict):
    for section in config:
      if section not in config_candidate:
        save_config(section, config[section])
        print('Section', section, 'of config is reset.')
      for option in config[section]:
        if option not in config_candidate[section]:
          save_config(section, config[section])
          print('Section', section, 'of config is reset.')
    print('Config read successfully.')
    config = config_candidate
  else:
    save_configs()
    print('config is reset.')

class WebFetcher:
  url: str = None
  cookies: dict|str = None
  year: int = None
  term: int = None
  # Maps for query
  key_map = {
    "year": "xnm",
    "term": "xqm",
    "action_type": "kzlx",
    "action": "ck"
  }
  term_map = {
    1: "3",
    2: "12"
  }

  def __init__(self, year, term):
    '''
      Set up variables of WebFetcher
    '''
    config_local = config['WebFetcher']
    self.url = config_local['url']
    self.cookies = config_local['cookies']
    if not (year and term):
      self.infer_term()
    if year: self.year = year
    if term: self.term = term

  def infer_term(self):
    '''
      Infer the school year and term based on system time now
    '''
    from datetime import datetime
    time_now = datetime.now()
    if 1 < time_now.month < 8:
      self.year = time_now.year-1
      self.term = 2
    else:
      self.year = time_now.year
      self.term = 1

  def get_data(self):
    payload = {
      self.key_map['year']: str(self.year),
      self.key_map['term']: self.term_map[self.term],
      self.key_map['action_type']: self.key_map['action']
    }
    if not isinstance(self.cookies, dict):
      if isinstance(self.cookies, str) and "=" in self.cookies:
        self.cookies = dict(item.split("=", 1) for item in self.cookies.split("; "))
      else:
        print('[Warning] The cookie jar is invalid.')
        self.cookies = {}
    import requests
    try:
      response = requests.post(self.url, data=payload, cookies=self.cookies)
    except requests.exceptions.RequestException as e:
      print(e)
      return None
    if response.status_code==200:
      try:
        return json.loads(response.text)
      except json.decoder.JSONDecodeError:
        print('[Error] Response from', self.url, 'is not a valid json.')
        print('Please check if you have configured the correct URL and Cookies.')
        return response.text
    else:
      print('[Error] Access to', self.url, 'is denied. Status Code', response.status_code)
      return response.status_code

class FormatConverter:
  max_idx: int = None
  max_weeks: int = None
  # convert_type = 1
  symbols = {'week': '周', 'range': '-', 'odd': '(单)', 'even': '(双)'}

  def __init__(self):
    config_local = config['FormatConverter']
    self.max_idx = int(config_local['max_idx'])
    self.max_weeks = int(config_local['max_weeks'])

  def convert_course(self, source_list: list[dict]):
    '''
      Deal with the course list
    '''
    courses = []
    # Map of direct converting
    translate_map = {"name": "kcmc", "teacher": "xm", "place": "cdmc"}
    convert_map = {"day": "xqj", "str_idx_range": "jcs", "str_weeks_range": "zcd"}
    for old_course in source_list:
      new_course = {}
      # Convert attributes that don't have to modify
      try:
        for new_key, old_key in translate_map.items():
          new_course[new_key] = old_course[old_key] if old_key in old_course else 'Unknown'
        # Day in a week
        new_course['day'] = int(old_course[convert_map['day']]) - 1
        # Course number
        start_idx, end_idx = str(old_course[convert_map['str_idx_range']]).split(self.symbols['range'], 2)
      except KeyError as e:
        print('[Warning] Critical information is wrong or missing,', e)
        continue
      new_course['start_idx'] = max(int(start_idx), 0)
      new_course['end_idx'] = min(int(end_idx), self.max_idx)
      new_course['start_time'] = 0
      new_course['end_time'] = 0
      new_course['use_idx'] = True
      # Weeks
      week_ls = str(old_course[convert_map['str_weeks_range']]).replace(self.symbols['week'], '').split(',')
      weeks = []
      for week_str in week_ls:
        # If this week item is a range...
        if self.symbols['range'] in week_str:
          step = 1
          start_week, end_week = week_str.split(self.symbols['range'], 2)
          start_week = int(start_week)
          # Deal with weeks in odd/even numbers
          if self.symbols['odd'] in end_week:
            if start_week%2==0: start_week+=1
            step = 2
            end_week = end_week.replace(self.symbols['odd'], '')
          elif self.symbols['even'] in end_week:
            if start_week%2!=0: start_week+=1
            step = 2
            end_week = end_week.replace(self.symbols['even'], '')
          for w in range(start_week, int(end_week)+1, step):
            weeks.append(str(w))
        # If it's one single week
        else:
          weeks.append(week_str)
      '''
      # Automatically increase max_weeks so that no lesson will be missing
      if int(weeks[-1]) > max_weeks:
        max_weeks = int(weeks[-1])
      '''
      new_course['weeks'] = weeks
      # Append to the target course list
      courses.append(new_course)
    return courses

  def get_start_date(self, year: int|str, term: str|int = '1'):
    '''
      Infer your new term start date
    '''
    year = int(year); month = 9; day = 1
    if str(term) == '2':
      year+=1
      month=3
    import datetime
    presumed_date = datetime.date(year, month, day)
    real_date = presumed_date-datetime.timedelta(days=presumed_date.weekday())
    return real_date.strftime("%Y-%#m-%#d")
   
  def convert_timetable(self, data: dict):
    '''
      Convert your original timetable data to OneCrouse-formatted data
    '''
    # Default information when data cannot be fetched
    school_year = 'Unknown School Year'
    school_term = 'Unknown School Term'
    year_int = 2000
    course_list = []
    # Try to fetch data
    try:
      year_int = int(data['xsxx']['XNM'])
      school_year = data['xsxx']['XNMC']
      school_term = data['xsxx']['XQMMC']
    except KeyError as e:
      print("School year information cannot be found.")
      print(e, f"Reset to {school_year} ({school_term})")
    try:
      course_list = data["kbList"]
    except KeyError:
      print("Course list not found")
    course_table = {'name': f'{school_year} ({school_term})',
            'start_date': self.get_start_date(year_int),
            "max_weeks": self.max_weeks,
            "time_table_name": "",
            "color_set": {},
            'courses': self.convert_course(course_list)}
    print('Convertion has been successfully done.')
    return course_table

def save_json(data: object, file_path: str = None, indent: int|str|None = None):
  '''
    Save a `.json`-like data file
  '''
  if not file_path:
    file_path = 'Saved File.json'
  try:
    with open(file_path, 'w+', encoding='utf-8', newline='\n') as f:
      json.dump(data, f, indent=indent, ensure_ascii=False)
    print('Successfully save as file:', file_path)
    return True
  except OSError as e:
    print(e)
  return False

def load_json(file_path: str):
  '''
    load a `.json`-like data file
  '''
  try:
    with open(file_path) as f:
      data = json.load(f)
    print('Successfully load file:', file_path)
    return data
  except OSError as e:
    print(e)
  return {}

def get_data_from_web(year: str|int = None, term: str|int = None):
  fetcher = WebFetcher(year, term)
  # Make sure the term is valid
  if term not in fetcher.term_map:
    fetcher.term = 1
  # If not both year and term exist
  if not (year and term):
    fetcher.infer_term()
  return fetcher.get_data()

def commands(year: int, term: int, input_file: str = None, output_file: str = None, convert: bool = True, display: bool = False):
  '''
    Convert your original timetable file (`.json`) to OneCrouse raw data file (`.cosx`)
  '''
  data = {}
  ext = 'json'
  # Get source data from local file
  if input_file:
    data = load_json(input_file)
  # Get source data online
  else:
    data = get_data_from_web(year, term)
  # If we decide to convert it
  if convert:
    if isinstance(data, dict):
      converter = FormatConverter()
      data = converter.convert_timetable(data)
      ext = 'cosx'
    # If source data is bad
    else:
      print('Source data is invalid, failed to convert.')
      # Ask whether to save the bad data, if it's from web
      if not input_file:
        save_invalid_web_data = input('Would you like to save the invalid data from web? (Y/N) ')
        if save_invalid_web_data in YES_TUPLE:
          try:
            with open('InvalidDataFromWeb.txt', 'wt+', encoding='utf-8', newline='\n') as f:
              f.write(str(data))
              print('The invalid data from web is successfully saved.')
          except OSError as e:
            print(e)
        else:
          print('User cancelled invalid data saving.')
      return False
  if display:
    print(json.dumps(data, ensure_ascii=False, indent=2) if isinstance(data, dict) else data)
    return True
  elif not output_file:
    if input_file:
      output_file = input_file.replace('.json', '.cosx') if '.json' in input_file else f'{input_file}.json'
    elif 'name' in data:
      output_file = '.'.join((data['name'], ext))
    elif 'xsxx' in data:
      try:
        output_file = '.'.join((f'{data['xsxx']['XNMC']} ({data['xsxx']['XQMMC']})', ext))
      except KeyError:
        output_file = '.'.join(('What', ext))
    else:
      output_file = '.'.join(('Unnamed', ext))
  save_json(data, output_file)
  return True

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(prog='FormatConverter')
  subparsers = parser.add_subparsers(dest='command', help='Available subcommands')

  # convert to save or print
  parser_convert = subparsers.add_parser('convert', help='get data from web or local and convert')
  parser_convert.add_argument('-y', '--year', type=int, help='School year')
  parser_convert.add_argument('-t', '--term', type=int, help='School term')
  parser_convert.add_argument('-i', '--input', type=str, help='input file path')
  parser_convert.add_argument('-o', '--output', type=str, help='output file path')
  parser_convert.add_argument("-d", "--display", action="store_true",
          help="display the converted timetable, instead of saving it")
  
  # get data to save or print
  parser_fetch = subparsers.add_parser('fetch', help='get data from web or local')
  parser_fetch.add_argument('-y', '--year', type=int, help='School year')
  parser_fetch.add_argument('-t', '--term', type=int, help='School term')
  parser_fetch.add_argument('-i', '--input', type=str, help='input file path')
  parser_fetch.add_argument('-o', '--output', type=str, help='output file path')
  parser_fetch.add_argument("-d", "--display", action="store_true",
          help="display the raw data file, instead of saving it")

  # show, update or reset the config
  parser_config = subparsers.add_parser('config', help='show, update or reset your config')
  parser_config.add_argument('-u', '--url', type=str, help='School lesson URL')
  parser_config.add_argument('-c', '--cookies', type=str, help='Cookie jar of yours')
  parser_config.add_argument('-i', '--index', type=int, help='Max index')
  parser_config.add_argument('-w', '--weeks', type=int, help='max weeks')
  parser_config.add_argument('--reset', action="store_true", help='Reset the config')

  read_configs()

  args = parser.parse_args()

  if args.command == 'convert':
    commands(year=args.year, term=args.term, input_file=args.input,
         output_file=args.output, convert=True, display=args.display)
  elif args.command == 'fetch':
    commands(year=args.year, term=args.term, input_file=args.input,
         output_file=args.output, convert=False, display=args.display)
  elif args.command == 'config':
    # args_config = parser_config.parse_args()
    if args.reset:
      yes_or_no = input('Are you sure to reset the config file? (Y/N)\n')
      if yes_or_no in YES_TUPLE:
        save_configs()
        print('Reset is done.')
      else:
        print('Reset cancelled.')
    else:
      if (args.url or args.cookies or args.index or args.weeks):
        if args.url:
          config['WebFetcher']['url'] = args.url
        if args.cookies:
          config['WebFetcher']['cookies'] = args.cookies
        if args.index:
          config['FormatConverter']['max_idx'] = args.index
        if args.weeks:
          config['FormatConverter']['max_weeks'] = args.weeks
        save_configs()
      if not (args.url or args.cookies or args.index or args.weeks):
        show_configs()
  else:
    parser.print_help()
