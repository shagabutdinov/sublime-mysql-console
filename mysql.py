import sublime

from Expression import expression
import subprocess
import time
import re
import os

def extract_query(view, sel):
  if not sel.empty():
    query_start, query_end = sel.begin(), sel.end()
  else:
    point = sel.a
    if view.substr(sublime.Region(point - 1, point)) == ';':
      point -= 1

    if view.substr(sublime.Region(point - 2, point)) == '; ':
      point -= 2

    if view.substr(sublime.Region(point - 2, point)) == '\G':
      point -= 2

    query_start = expression.find_match(
      view,
      point,
      r'(\\g|\\G|;|^)',
      {'backward': True},
    )

    if query_start == None:
      return None, None, None

    query_start = query_start.end(1)

    query_end = expression.find_match(view, point, r'(\\g|\\G|;|$)')
    if query_end == None:
      return None, None, None

    query_end = query_end.end(1)

  query = view.substr(sublime.Region(query_start, query_end))
  query_start += len(re.search('^(\s*)', query).group(1))

  return query.strip(), query_start, query_end

def run_query(view, query, expand = False, options = []):
  settings = view.settings().get('mysql', None)
  if settings != None:
    if expand and query.endswith(';'):
      query = query[:-1] + '\G'

    return run_sql_query(settings + ['-e', query] + options)

  settings = view.settings().get('pgsql', None)
  if settings != None:
    if isinstance(query, list):
      new_query = []
      for part in query:
        new_query = new_query + ['--command', part]

      query = new_query
    else:
      if expand:
        options = options + ['--expanded']
      elif query.endswith('\G'):
        options = options + ['--expanded']
        query = query[:-2]

      if query.endswith(';'):
        query = query[:-1]

      query = ['--command', query]

    command = settings + query + options
    return run_sql_query(command, view.settings().get('pgsql_password', None))

  raise Exception(
    'mysql or pgsql should be set in project or global settings',
  )

def run_sql_query(command, password = ''):
  try:
    result = subprocess.check_output(
      command,
      stderr = subprocess.STDOUT,
      env = dict(os.environ, **{'PGPASSWORD': password})
    )

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
  if view.settings().get('mysql', None) != None:
    tables = _get_mysql_tables(view)
    return _get_mysql_fields(view, tables)

  if view.settings().get('pgsql', None) != None:
    tables = _get_pgsql_tables(view)
    return _get_pgsql_fields(view, tables)

  raise Exception(
    'mysql or pgsql should be set in project or global settings',
  )

def _get_mysql_tables(view):
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

def _get_mysql_fields(view, tables):
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

def _get_pgsql_tables(view):
  success, result = run_query(view, '\d')

  if not success:
    raise Exception('Query error: ' + result)

  tables = []
  for line in result.split('+')[3].split("\n"):
    expr = r'^.*\|\s*(\w+)\s*\|\s*table.*$'
    if re.match(expr, line) == None:
      continue

    table = re.sub(expr, '\\1', line)
    if table == '':
      continue

    tables.append(table)

  return tables

def _get_pgsql_fields(view, tables):
  query = []
  for table in tables:
    query.append('\d ' + table)

  if len(query) == 0:
    return {}

  success, result = run_query(view, query)
  tables_with_fields = re.split(r'Table ', result)[1:]

  result = {}
  for table_with_field in tables_with_fields:
    table_name = re.search(r'^".*?\.(.+?)"', table_with_field).group(1)
    fields = re.findall(r'\n\s*(\w+)\s*\|\s*(.+?)\s*\|', table_with_field)
    result[table_name] = {'fields': {}}
    for field in fields:
      if field[0] == 'Column':
        continue

      result[table_name]['fields'][field[0]] = field[1]

  return result

