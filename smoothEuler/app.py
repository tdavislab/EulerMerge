from flask import Flask, render_template, jsonify, request
from util import process_Edge_strs, get_connect_path, load_set_path_dict_file
# Boiler plate stuff to start the module
import jpype
import jpype.imports
from jpype.types import *
import copy
import networkx as nx
import json
import matplotlib.pyplot as plt
import csv 
from dataTransformer import EulerDataTransformer

app = Flask(__name__)

# Launch the JVM
jpype.startJVM(classpath=['java/*'])

# several global variables
folder_name = 'testExample'
subfolder_name = 'step0'
set_path_dict = ''


SampleClass = JClass("main.MainApplication")()
SampleClass.loadGraph(10, 15, 'testExample', 'step1')

@app.route("/")
def index():
  return render_template("index.html")

# when load the page, get the folder name, init the set_path_dict
@app.route("/init", methods=['POST'])
def init():
  global folder_name, set_path_dict
  request_data = request.get_json() 
  folder_name = request_data['dataName']
  return ('', 204)

@app.route("/smooth", methods=['POST'])
def smooth():
  request_data = request.get_json()
  print(request_data)
  global set_path_dict, folder_name, subfolder_name
  iteration = request_data['iteration']
  distance = request_data['distance']
  subfolder_name = request_data['step']
  set_path_dict = load_set_path_dict_file(folder_name, subfolder_name)
  SampleClass = JClass("main.MainApplication")()
  SampleClass.loadGraph(iteration, distance, JString(folder_name), JString(subfolder_name))
  SampleClass.runSmoothGraph()
  edge_strs = str(SampleClass.getEdgeNodes())
  return jsonify(get_connect_path(process_Edge_strs(edge_strs), set_path_dict))

if __name__ == '__main__':
  # first process the unsmoothed simplified euler data
  pre_path = './static/data/eulerData'
  eulerDataTransformer = EulerDataTransformer(pre_path)
  eulerDataTransformer.transformer()
  eulerDataTransformer.write_to_file()
  eulerDataTransformer.write_set_path_dict_file()
  print("preprocess done")
  app.run(debug = True)
