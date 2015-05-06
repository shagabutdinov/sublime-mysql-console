import sublime
import sublime_plugin

from . import mysql
import re

class MysqlCompletions(sublime_plugin.EventListener):
  def on_query_completions(self, view, prefix, locations):
    info = mysql.get_info(view)

    result = []
    for location in locations:
      result += self._get_completions(info, view, prefix, location)

    return result

  def _get_completions(self, info, view, prefix, location):
    result = []
    beginner = view.substr(sublime.Region(view.line(location).a, location))

    quote = re.search(r'(`?)\w*$', beginner).group(1)
    if quote == '`':
      quote = ''
    else:
      quote = '`'

    query = mysql.extract_query(view, sublime.Region(location, location))
    tables_in_query = re.findall(r'(?:TABLE|FROM|INTO|UPDATE|JOIN) `(.*?)`',
      query[0])

    match = re.search(r'(?:TABLE|FROM|INTO|UPDATE|JOIN)\s*`\w*$', beginner)

    if match != None:
      result = []
      for table in sorted(list(info.keys())):
        if self._check_prefix(prefix, table):
          result.append((table, table))
    else:
      for table in tables_in_query:
        if table == '' or table not in info:
          continue

        for field in list(info[table]['fields'].keys()):
          if self._check_prefix(prefix, field):
            result.append((table + ': ' + field, quote + field + quote))

    for table in tables_in_query:
      if self._check_prefix(prefix, table):
        result.append((table, quote + table + quote))

    return result

  def _check_prefix(self, prefix, word):
    if word == '':
      return False

    if prefix == '':
      return True

    return re.search('^' + '.*'.join(list(prefix)), word) != None