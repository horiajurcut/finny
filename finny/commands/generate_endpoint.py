import os
import sys 

import json

from importlib import import_module

from jinja2 import Environment, PackageLoader
from finny.command import Command

import inflect
import imp

class GenerateEndpoint(Command):

  def __init__(self):
    self.pluralize = inflect.engine()

  def _touch(self, filepath):
    open(filepath, 'a').close()

  def run(self, params):
    self.params = params

    cwd = os.getcwd()

    config = imp.new_module('config')
    config.__file__ = "config"
    # loads the configuration file
    with open(cwd + "/__init__.py") as config_file:
      exec(compile(config_file.read(), "config", 'exec'), config.__dict__)

    self.app_name = config.__APP__

    endpoint_path = cwd + "/resources/" + params.name
    # create folder for endpoint
    os.makedirs(endpoint_path)

    # copy templates over
    self._copy_templates([ "api.py", "model.py"], "endpoint", endpoint_path)

    self.read_default_runner()

  def read_default_runner(self):
    cwd = os.getcwd() + "/resources"

    endpoints = [ name for name in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, name)) ]

    cwd = os.getcwd()

    with open("%s/%s/runners/default.py" % (cwd, self.app_name), "w+") as f:
      f.write("ENDPOINTS = %s" % json.dumps(endpoints))

  def _copy_templates(self, source, src, dst):
    env = Environment(loader=PackageLoader('finny.commands', 'templates/' + src))

    for item in source:
      template = env.get_template("%s.jinja" % item)
      output = template.render(name=self.params.name,
                               plural_name=self.pluralize.plural(self.params.name),
                               app_name=self.app_name)

      path = dst + "/" + item
      dirname = os.path.dirname(path)

      if not os.path.exists(dirname):
        os.makedirs(dirname)

      self._touch(dirname + "/__init__.py")

      with open(path, "w+") as f:
        f.write(output)
