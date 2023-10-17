import copy
import json

# process the edge_strs into {'a': [{"x": 333, "y": 264}, ...], }
# process edge_strs into {'0_e': [{"x": 333, "y": 264}, ...]}
def process_Edge_strs(edge_strs):
    res = {}
    edge_str_lst = edge_strs.strip().split('\t')
    for edge_str in edge_str_lst:
        name_coord = edge_str.split('*')
        name = name_coord[0]
        res[name] = []
        coords = name_coord[1].strip()
        for coord_lst in coords.split(' '):
          coord = coord_lst.split(',')
          res[name].append({"x": coord[0], "y": coord[1]})
    return res

# according to the set_path_dict, connect all path, return [{"curve": {"name":"a", "coordinates": []}}]
def get_connect_path(edge_dict, set_path_dict_para): 
  set_path_dict = copy.deepcopy(set_path_dict_para)
  res = []
  for key in set_path_dict:
    sub_res = {"curve": {"name": key, "coordinates": ''}}
    edge_id_lst = set_path_dict[key]
    pre_edge_lst = edge_dict[edge_id_lst.pop(0)]
    while len(edge_id_lst)!=0:
        last_node = pre_edge_lst[-1]
        for idx, edge_id in enumerate(edge_id_lst):
          edge = edge_dict[edge_id]
          if last_node['x'] == edge[0]['x'] and last_node['y'] == edge[0]['y']:
              pre_edge_lst += edge[1:]
              edge_id_lst.pop(idx)
              break
          elif last_node['x'] == edge[-1]['x'] and last_node['y'] == edge[-1]['y']:
            edge.reverse()
            pre_edge_lst += edge[1:]
            edge_id_lst.pop(idx)
            break
    sub_res['curve']['coordinates'] = copy.deepcopy(pre_edge_lst[:-1])
    res.append(sub_res)
  return res


def load_set_path_dict_file(folder_name, subfolder_name):
  set_path_dict = ''
  with open('./static/data/'+folder_name+'/'+subfolder_name+'/setPathDict.json', 'r') as f:
    set_path_dict = json.load(f)
  return set_path_dict