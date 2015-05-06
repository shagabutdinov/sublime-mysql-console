import sublime
import sublime_plugin

try:
  from Context.base import Base
except ImportError:
  sublime.error_message("Dependency import failed; please read readme for " +
   "ScopeContext plugin for installation instructions; to disable this " +
   "message remove this plugin")

from . import mysql
import re

class MysqlQueryContext(Base):

  def on_query_context(self, *args):
    return self._check_sel('mysql_query', self._callback, *args)

  def _callback(self, view, sel):
    if re.search(r'source\.sql', view.scope_name(sel.begin())) == None:
      return None

    query = mysql.extract_query(view, sel)
    if query == None:
      return None

    return query[0]