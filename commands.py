import sublime
import sublime_plugin

from . import mysql
import re

class RunMysqlQuery(sublime_plugin.TextCommand):
  def run(self, edit, replace = False, append = False, expand = False):
    result = []
    for sel in reversed(self.view.sel()):
      result.append(self._run(edit, sel, replace, append, expand))

      if len(self.view.sel()) == 1:
        self.view.show(self.view.sel()[0].a)

  def _run(self, edit, sel, replace, append, expand):
    query, query_start, query_end = mysql.extract_query(self.view, sel)
    if query == None:
      return

    _, result = mysql.run_query(self.view, query, expand)

    if replace:
      self.view.replace(
        edit,
        sublime.Region(query_start, query_end),
        result + ";\n\n"
      )
    elif append:
      self.view.insert(
        edit,
        query_end,
        "\n\n" + result + ";\n\n"
      )
    else:
      output = self.view.window().create_output_panel('run_mysql_query_result')

      output.set_read_only(False)
      output.run_command('append', {
        'characters': result,
      })

      output.set_read_only(True)

      self.view.window().run_command("show_panel", {
        "panel": "output." + 'run_mysql_query_result'
      })

      output.sel().clear()

class OpenMysqlConsole(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view.window().new_file()
    view.set_scratch(True)
    view.set_syntax_file('Packages/SQL/SQL.tmLanguage')
    view.settings().set('auto_complete', True)
    view.settings().set('auto_complete_triggers', [
      {
        "characters": "`",
        "selector": "source.sql"
      }
    ])
