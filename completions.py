import sublime
import sublime_plugin

from threading import Thread

from . import mysql
import re

info = None

class UpdateInfo(Thread):

  def __init__(self, view):
    Thread.__init__(self)
    self.view = view

  def run(self):
    info = mysql.get_info(self.view)


class MysqlCompletions(sublime_plugin.EventListener):
  def on_query_completions(self, view, prefix, locations):
    global info
    scope = view.scope_name(view.sel()[0].begin())
    if re.search(r'source\.sql', scope) == None:
      return None

    escape = ''
    if view.settings().get('mysql', None) != None:
      escape = '`'
    elif view.settings().get('pgsql', None) != None:
      escape = '"'
    else:
      return None

    if info == None:
      info = mysql.get_info(view)
    else:
      UpdateInfo(view).start()

    result = []
    for location in locations:
      result += self._get_completions(info, view, prefix, location, escape)

    if len(result) == 0:
      return []

    return (
      result,
      sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS
    )

  def _get_completions(self, info, view, prefix, location, escape):
    result = []
    beginner = view.substr(sublime.Region(max(location - 512, 0), location))

    quote = re.search(r'(' + escape + '?)\w*$', beginner)
    if quote != None:
      quote = quote.group(1)

    if quote == escape:
      quote = ''
    else:
      quote = escape

    escape_with_question = ''
    if escape != '':
      escape_with_question = escape + '?'

    query = mysql.extract_query(view, sublime.Region(location, location))
    tables_in_query = re.findall(
      r'(?:TABLE|FROM|INTO|UPDATE|JOIN)\s+' +
        escape_with_question +
        '(\w+)' +
        '(?:' + escape_with_question + '|[\s;])',
       query[0]
    )

    match = re.search(
      r'(?:TABLE|FROM|INTO|UPDATE|JOIN)(\s*[\w\.]+\s*,\s*)?\s*' +
        escape_with_question + '\w*$',
      beginner
    )

    if match != None:
      result = []
      for table in sorted(list(info.keys())):
        if self._check_prefix(prefix, table):
          result.append((table, table))
    else:
      prefix_table = re.search(
        r'' +
        escape_with_question +
          r'(\w+)' +
          escape_with_question +
          '\.' +
          escape_with_question +
          '\w*$',
        beginner
      )

      if prefix_table != None:
        for field in list(info[prefix_table.group(1)]['fields'].keys()):
          if self._check_prefix(prefix, field):
            result.append((field, quote + field + quote))
      else:
        for table in tables_in_query:
          if table not in info:
            continue

          completion_prefix = ''
          if 'UPDATE' not in query[0]:
            completion_prefix = quote + table + quote + '.'

          for field in list(info[table]['fields'].keys()):
            if self._check_prefix(prefix, field):
              result.append((
                table + ': ' + field,
                completion_prefix + quote + field + quote
              ))

    for table in tables_in_query:
      if self._check_prefix(prefix, table):
        result.append((table, quote + table + quote))

    return result

  def _check_prefix(self, prefix, word):
    if word == '' or prefix == word:
      return False

    if prefix == '':
      return True

    return re.search('^' + '.*'.join(list(prefix)), word) != None
