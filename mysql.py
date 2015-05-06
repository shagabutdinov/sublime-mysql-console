import sublime

from Expression import expression
import subprocess
import time
import re

def extract_query(view, sel):
  if not sel.empty():
    query_start, query_end = sel.begin(), sel.end()
  else:
    point = sel.a
    if view.substr(sublime.Region(point - 1, point)) == ';':
      point -= 1

    if view.substr(sublime.Region(point - 2, point)) == '\G':
      point -= 2

    query_start = (expression.find_match(view, point, r'(\\g|\\G|;|^)',
        {'backward': True}).end(1))

    query_end = (expression.find_match(view, point, r'(\\g|\\G|;|$)').
      end(1))

  query = view.substr(sublime.Region(query_start, query_end))
  query_start += len(re.search('^(\s*)', query).group(1))

  return query, query_start, query_end

def run_query(view, query, options = []):
  try:
    mysql = view.settings().get('mysql', None)
    if mysql == None:
      raise Exception("mysql should be set in project or global settings")

    result = subprocess.check_output(mysql + ['-e', query] + options,
      stderr = subprocess.STDOUT)

    success = True
    result = result.decode('utf-8')

    if result.strip() == '':
      result = 'OK ' + time.strftime("%H:%M:%S")
  except UnicodeDecodeError:
    result = result.decode('unicode_escape')
  except subprocess.CalledProcessError as error:
    result = error.output.decode('utf-8')
    success = False

  return success, result

def get_info(view):
  tables = _get_tables(view)
  result = _get_fields(view, tables)
  return result

def _get_fields(view, tables):
  query = []
  for table in tables:
    query.append('SHOW CREATE TABLE `' + table + '`')

  success, result = run_query(view, '\\G'.join(query) + '\G')
  tables_with_fields = re.split(r'Create Table: ', result)[1:]

  result = {}
  for table_with_field in tables_with_fields:
    table_name = re.search(r'CREATE TABLE `(.+?)`', table_with_field).group(1)
    fields = re.findall(r'\n\s*`(.+?)`\s*(.+?)(?:,|\n\))', table_with_field)
    result[table_name] = {'fields': {}}
    for field in fields:
      result[table_name]['fields'][field[0]] = field[1]

  return result

def _get_tables(view):
  success, result = run_query(view, 'SHOW TABLES')

  if not success:
    raise Exception('Query error: ' + result)

  tables = []
  for line in result.split('+')[4].split('\n'):
    table = re.sub(r'^\|\s*(.*?)\s*\|$', '\\1', line)
    if table == '':
      continue

    tables.append(table)

  return tables