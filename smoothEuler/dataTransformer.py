# transform the original data into the structure of EulerSmooth
'''
Overall Graph
    1. Nodes: 
        get the name and coordinates from abstractDiagram (element nodes);
        get the crossing nodes by computing the intersections
        label nodes where it belongs to
    2. Edges:
        insert the intersections into set curve, and split it into path segments, label which set it belongs to
Initial structure
{
    sets: {
        'a':{nodes: [nodename, ...], edges: [edgename, ...], points: [{x: , y: }, ...]},
        'b':...
    }
    nodes:{
        nodesName:{x: , y: , isIntersect: 1/0}
        nodesName:{x: , y: , isIntersect: 1/0}
        ...
    }
    edges:{
        edgeName:{from: nodeName, to: nodeName, edgePoints:[{x: y: }, ....]}
    }
}
According to the Initial structure, we then get the .oco file
'''

from itertools import combinations
from shapely.geometry import LineString
import copy
import csv
import json
import math

# https://github.com/renatav/GraphDrawing/blob/de84478ec24bf0bdf1ab54c3f0989f67d77645dc/GraphDrawingTheory/src/graph/algorithms/planarity/PlanarEmbedding.java

'''
Transform the JSON data of Euler Diagram into the .oco file that will be the input of the EulerSmooth Data
'''
class EulerDataTransformer:
    def __init__(self, pre_path):
        self.pre_path = pre_path
        self.json_data = ''
        self.json_data_sep = '' # sets info in the euler data that has the seperation
        self.intersect_id = 0
        self.edge_id = 0
        self.init_struct = {
            'sets': {},
            'nodes': {},
            'edges': {},
            'zoneGraph': []    # zone graph 
        }
        self.sets_sep = {}  # sets info in the euler data that has the seperation
    
    # transform the json data into the init_struct
    def transformer(self):
        self.load_data()
        self.init_init_struct()
        # check if the two json files have the same number of points for each set
        for key in self.init_struct['sets']:
            set_src_2 = self.sets_sep[key]
            if len(self.init_struct['sets'][key]['points']) != len(set_src_2['points']):
                print('the nodes are not the same!')

        self.intersection_handler()
        
        self.checkIndependentSet()

        # for key in self.init_struct['sets']:
        #     print(key)
        #     print(self.init_struct['sets'][key]['points'])

        # replace points
        self.replace_points()

        # for key in self.init_struct['sets']:
        #     print(key)
        #     print(self.init_struct['sets'][key]['points'])

        self.edge_handler()
        # print(self.init_struct['nodes'])


    def replace_points(self):
        '''merge points for each set in the separate format and non-separate format
        intersect {x: y: name: replace: }
        '''
        sets_non_sep = self.init_struct['sets']
        sets_sep = self.sets_sep
        for set in sets_non_sep:
            new_points = []
            set_points_non_sep = sets_non_sep[set]['points']
            set_points_sep = sets_sep[set]['points']
            idx = 0
            for item in set_points_non_sep:
                if 'name' not in item:  # general points
                    new_points.append(set_points_sep[idx])
                    idx+=1
                elif 'replace' not in item: # add new points
                    new_points.append(item)
                else:   # replace
                    new_points.append(item)
                    idx += 1
            sets_non_sep[set]['points'] = new_points
            # print(set)
            # print(new_points)

    # load the json data
    def load_data(self):
        with open(self.pre_path+'/EulerJSON-0.json', 'r') as f:
            self.json_data = json.load(f)
        with open(self.pre_path+'/EulerJSON-2.json', 'r') as f:
            self.json_data_sep = json.load(f)

    # check if the node in the Nodes set
    def nodeInNodes(self, node):
        for Node in self.init_struct['nodes'].values():
            if node['x'] == Node['x'] and node['y'] == Node['y']:
                return True
        return False

    # init the data of 'init_struct'
    def init_init_struct(self):
        # 1. init sets
        for set_obj in self.json_data['curves']:
            set_name = set_obj['curve']['name']
            self.init_struct['sets'][set_name] = {'nodes': [], 'edges': [], 'points': set_obj['curve']['coordinates']}
        # 2. init element nodes
        for ele_node in self.json_data['abstractDiagram']:
            node_name = ele_node['zone']+'_n'
            coordinate = ele_node['coordinate']
            self.init_struct['nodes'][node_name] = {'x': coordinate['x'], 'y': coordinate['y'], 'isIntersect': 0}
            # add node_name into 'set'(here the nodes are zones)
            for key in self.init_struct['sets']:
                if key in ele_node['zone']:
                    self.init_struct['sets'][key]['nodes'].append(node_name)
        # 3. init the zone graph
        self.init_struct['zoneGraph'] = self.json_data['zoneGraph']
        # 4. init the set information for the separation data
        for set_obj in self.json_data_sep['curves']:
            set_name = set_obj['curve']['name']
            self.sets_sep[set_name] = {'nodes': [], 'edges': [], 'points': set_obj['curve']['coordinates']}


    def lineIntersect(self, seg_A, seg_B):
        '''get the intersections of two line segments
        if no intersections, segment coincide, or having one intersection but two line are almost parallel return false

        Returns:
            False / {'x': intersection.x, 'y': intersection.y, 'isIntersect': 1}
        '''
        line1 = LineString([(seg_A[0]['x'], seg_A[0]['y']), (seg_A[1]['x'], seg_A[1]['y'])])
        line2 = LineString([(seg_B[0]['x'], seg_B[0]['y']), (seg_B[1]['x'], seg_B[1]['y'])])
        # check if the two lines almost parallel
        slope_line1 =math.atan(abs((seg_A[1]['y']-seg_A[0]['y'])/(seg_A[1]['x']-seg_A[0]['x']))) if seg_A[1]['x']-seg_A[0]['x']!=0 else math.atan(math.inf)
        slope_line2 =math.atan(abs((seg_B[1]['y']-seg_B[0]['y'])/(seg_B[1]['x']-seg_B[0]['x']))) if seg_B[1]['x']-seg_B[0]['x']!=0 else math.atan(math.inf)
        if abs(slope_line1-slope_line2)<0.05: 
            print('skip')
            return False
        intersect = line1.intersects(line2) 
        if not intersect:
            return False
        else:
            try:
                intersection = line1.intersection(line2)
                intersect_node = {'x': intersection.x, 'y': intersection.y, 'isIntersect': 1}
                return intersect_node
            except:
                return False
    
    def checkIntersectExist(self, node):
        '''check if the node is in the self.init_struct['nodes']
        Args:
            node {'x': intersection.x, 'y': intersection.y, 'isIntersect': 1}: input node
        Returns:
            if not in => False
            if in => the node object
        '''
        for node_name in self.init_struct['nodes']:
            refer_node = self.init_struct['nodes'][node_name]
            if math.isclose(refer_node['x'], node['x']) and math.isclose(refer_node['y'], node['y']):
                return refer_node
        return False
    
    def is_valide_intersection(self, setA, setB, idA, idB, intersect):
        '''check if the intersection between [setA[idA], setA[idA+1]] and [setB[idB], setB[idB+1]] is valid or not
        valid: the intersection is not within this common area of setA and setB
        intersect: the intersection between the two elements
        '''
        # all related curve segments
        seg_A = [setA[idA], setA[idA+1]] if idA < len(setA)-1 else [setA[idA], setA[0]]
        seg_B = [setB[idB], setB[idB+1]] if idB < len(setB)-1 else [setB[idB], setB[0]]
        seg_A_last = [setA[idA-1], setA[idA]] if idA > 0 else [setA[-1], setA[0]]
        seg_B_last = [setB[idB-1], setB[idB]] if idB > 0 else [setB[-1], setB[0]]
        seg_A_next = ''
        if idA < len(setA)-2:
            seg_A_next = [setA[idA+1], setA[idA+2]]
        elif idA == len(setA)-2:
            seg_A_next = [setA[idA+1], setA[0]]
        elif idA == len(setA)-1:
            seg_A_next = [setA[0], setA[1]]
        seg_B_next = ''
        if idB < len(setB)-2:
            seg_B_next = [setB[idB+1], setB[idB+2]]
        elif idB == len(setB)-2:
            seg_B_next = [setB[idB+1], setB[0]]
        elif idB == len(setB)-1:
            seg_B_next = [setB[0], setB[1]]

        # check if the intersect at the start or end of a segment
        def check_pos_of_intersect(seg):
            if math.isclose(seg[0]['x'], intersect['x']) and math.isclose(seg[0]['y'], intersect['y']):
                return "start"
            if math.isclose(seg[1]['x'], intersect['x']) and math.isclose(seg[1]['y'], intersect['y']):
                return "end"
            return False    # at the center of segment, then this intersect is valid
        seg_A_pos = check_pos_of_intersect(seg_A)
        seg_B_pos = check_pos_of_intersect(seg_B)
        if not (seg_A_pos and seg_B_pos):   # if the intersect is not in one of the ends of the two segments, is valid
            return True

        # check if two line intersect at a line
        def check_coincide_lines(seg1, seg2):
            try: 
                line1 = LineString([(seg1[0]['x'], seg1[0]['y']), (seg1[1]['x'], seg1[1]['y'])])
                line2 = LineString([(seg2[0]['x'], seg2[0]['y']), (seg2[1]['x'], seg2[1]['y'])])
            except:
                print(seg2)
            intersection = line1.intersection(line2)
            inter_type = intersection.__class__.__name__
            if inter_type=='LineString':
                return True
            return False

        is_valid = True
        if seg_A_pos=="start" and seg_B_pos=="end":
            is_valid = not (check_coincide_lines(seg_A_last, seg_B) and check_coincide_lines(seg_A, seg_B_next))
        elif seg_A_pos=="start" and seg_B_pos=="start":
            is_valid = not (check_coincide_lines(seg_A_last, seg_B) and check_coincide_lines(seg_A, seg_B_last))
        elif seg_A_pos=="end" and seg_B_pos=="start":
            is_valid = not (check_coincide_lines(seg_A_next, seg_B) and check_coincide_lines(seg_A, seg_B_last))
        elif seg_A_pos=="end" and seg_B_pos=="end":
            is_valid = not (check_coincide_lines(seg_A_next, seg_B) and check_coincide_lines(seg_A, seg_B_next))
        return is_valid

    def remove_duplicate_point(self, set_lst):
        '''remove  duplicate points in setList (when a point is the same to an intersection, and they are adjacent, remove the poit)

        Args:
        set_lst ([obj,..]): a list of objects that include 2 kinds of points (general point){x:, y:} 
        and intersection {name: , x: , y: , intersect:1}

        Returns:
        set_lst 
        '''
        # special case:
        if 'name' in set_lst[-1]:
            last_point = set_lst[-1]
            point = set_lst[0] 
            if math.isclose(last_point['x'], point['x']) and math.isclose(last_point['y'], point['y']):
                # put the last one to the first
                last_point['replace']=1
                set_lst.pop()
                set_lst.insert(0, last_point)

        new_set = []
        for idx, point in enumerate(set_lst):
            pre_point = set_lst[idx-1] if idx != 0 else False
            post_point = set_lst[idx+1] if idx != len(set_lst)-1 else set_lst[0]
            if 'name' in point:
                new_set.append(point)
            else:
                if pre_point and 'name' in pre_point:
                    if math.isclose(pre_point['x'], point['x']) and math.isclose(pre_point['y'], point['y']):
                        pre_point['replace']=1
                        continue
                if 'name' in post_point:
                    if math.isclose(post_point['x'], point['x']) and math.isclose(post_point['y'], point['y']):
                        post_point['replace']=1
                        continue
                new_set.append(point)
        return new_set

    # insert the intersection into the data structure
    def insert_intersect_nodes(self, setA_name, setB_name):
        setA = self.init_struct['sets'][setA_name]['points']
        setB = self.init_struct['sets'][setB_name]['points']
        setA_rep = []
        setB_intersects = []  # the intersections of set B [idx, {intersect object}]
        setB_rep = copy.deepcopy(setB)

        intersect_num = 0
        for idA, _ in enumerate(setA):
            seg_A = [setA[idA], setA[idA+1]] if idA < len(setA)-1 else [setA[idA], setA[0]]
            setA_rep.append(copy.deepcopy(seg_A[0]))
            for idB, valB in enumerate(setB):
                seg_B = [setB[idB], setB[idB+1]] if idB < len(setB)-1 else [setB[idB], setB[0]]
                # test if has intersection
                intersect = self.lineIntersect(seg_A, seg_B)
                if intersect:
                    # check if the intersection are in the common area of two sets
                    if not self.is_valide_intersection(setA, setB, idA, idB, intersect):
                        print('find one invalid node')
                        continue
                    intersect_num += 1  # valid intersection
                    pre_intersect = self.checkIntersectExist(intersect) # check if this nodes already exists
                    name = ''
                    if pre_intersect:
                        name = pre_intersect['name']
                        intersect = pre_intersect
                    else:
                        name = str(self.intersect_id) + '_cn'
                        self.intersect_id += 1 
                        intersect['name'] = name
                        # append to total and seperate node list
                        self.init_struct['nodes'][name] = intersect

                    # if the two sets are concurrent
                    nodes_in_setA = self.init_struct['sets'][setA_name]['nodes'] # node name
                    nodes_in_setB = self.init_struct['sets'][setB_name]['nodes']
                    if name not in nodes_in_setA:
                        nodes_in_setA.append(name)
                        setA_rep.append(copy.deepcopy(intersect))
                    if name not in nodes_in_setB:
                        nodes_in_setB.append(name)
                        setB_intersects.append([idB+1, copy.deepcopy(intersect)])

        # init the set B        
        def efun(e):
            return e[0]
        setB_intersects.sort(key=efun)  # rank the setB_intersects according to the idx
        for idx, setB_intersect in enumerate(setB_intersects):  # insert it into setB
            setB_rep.insert(setB_intersect[0]+idx, setB_intersect[1])
        
        # remove the duplicate points in setA and setB (when a point is the same to an intersection, and they are adjacent, remove the poit)
        self.init_struct['sets'][setB_name]['points'] = self.remove_duplicate_point(setB_rep)
        self.init_struct['sets'][setA_name]['points'] = self.remove_duplicate_point(setA_rep)


    # handle the intersections of sets
    def intersection_handler(self):
        set_name_lst = list(self.init_struct['sets'].keys())
        set_pair_lst = list(combinations(set_name_lst, 2))
        # self.insert_intersect_nodes('a', 'f')
        for set_pair in set_pair_lst:
            self.insert_intersect_nodes(set_pair[0], set_pair[1])

    # check if a set is an independent component, if it is, pick an random point as adjunct point
    def checkIndependentSet(self):
        for set_key in self.init_struct['sets']:
            points = self.init_struct['sets'][set_key]['points']
            cn_idx_lst = []
            for idx, point in enumerate(points):
                if 'isIntersect' in point:
                    cn_idx_lst.append(idx)
            if len(cn_idx_lst) == 0:
                intersect =  copy.deepcopy(points[-1])    # pick the last one as ajunct point
                intersect['isIntersect'] = 1
                name = str(self.intersect_id) + '_cn'
                intersect['name'] = name
                self.intersect_id += 1
                # append to total and seperate node list
                self.init_struct['sets'][set_key]['points'][-1] = intersect
                self.init_struct['nodes'][name] = intersect
                self.init_struct['sets'][set_key]['nodes'].append(name)

    # init one edge
    def init_edge(self, points, set_key):
        cn_idx_lst = []
        for idx, point in enumerate(points):
            if 'isIntersect' in point:
                cn_idx_lst.append(idx)
        # init each edge not between the start and the end
        for idx, val in enumerate(cn_idx_lst):
            if idx == len(cn_idx_lst)-1:
                break
            edge_obj = {'from': '', 'to': '', 'edgePoints': ''}
            edge_name = str(self.edge_id)+'_e'
            self.edge_id += 1
            edge_obj['from'] = points[cn_idx_lst[idx]]['name']
            edge_obj['to'] = points[cn_idx_lst[idx+1]]['name']
            if abs(cn_idx_lst[idx]-cn_idx_lst[idx+1])!=1:
                edge_obj['edgePoints'] = points[cn_idx_lst[idx]+1: cn_idx_lst[idx+1]]
            self.init_struct['edges'][edge_name] = edge_obj
            self.init_struct['sets'][set_key]['edges'].append(edge_name)
        # add the first
        edge_obj = {'from': '', 'to': '', 'edgePoints': ''}
        edge_name = str(self.edge_id)+'_e'
        self.edge_id += 1
        edge_obj['from'] = points[cn_idx_lst[-1]]['name']
        edge_obj['to'] = points[cn_idx_lst[0]]['name']
        edge_obj['edgePoints'] = points[cn_idx_lst[-1]+1: len(points)]+points[0:cn_idx_lst[0]]
        self.init_struct['edges'][edge_name] = edge_obj
        self.init_struct['sets'][set_key]['edges'].append(edge_name)

    # process all edges into the init_struct
    def edge_handler(self):
        for set_key in self.init_struct['sets']:
            self.init_edge(self.init_struct['sets'][set_key]['points'], set_key)


    ###############################################################################
    ## Following methods handling the file writing
    ###############################################################################
    
    # get the nodes string
    def get_nodes_str(self):
        node_str = '#nodes\n'
        # add title
        node_lst = [['@attribute', 'nodePosition', 'color', 'nodeSize'],
                     ['@type', 'Coordinates', 'Color', 'Coordinates'], 
                     ['@default', '0.0,0.0', '#ff0000ff', '1.0,1.0']]
        # add nodes
        for key in self.init_struct['nodes']:
            node = self.init_struct['nodes'][key]
            node_lst.append([key, str(node['x'])+','+str(node['y']), '#ff0000ff', '5,5']) 
        # transform it into the file
        for row in node_lst:
            node_str += '\t'.join(row)
            node_str += '\n'
        return node_str+'\n\n'
        

    # get the edges string
    def get_edges_str(self):
        edge_str = '#edges\n'
        # add title
        edge_lst = [['@attribute', '@from', '@to', 'edgePoints'],
                    ['@type', '', '', 'ControlPoints'],
                    ['@default', '', '', '']]
        # add edges
        for key in self.init_struct['edges']:
            edge = self.init_struct['edges'][key]
            edgePoints = ''
            for idx, edgePoint in enumerate(edge['edgePoints']):
                edgePoints += str(edgePoint['x'])+','+str(edgePoint['y'])+','
                if idx != len(edge['edgePoints'])-1:
                    edgePoints += ' '
            edge_lst.append([key, edge['from'], edge['to'], edgePoints])
        # transform it into the file
        for row in edge_lst:
            edge_str += '\t'.join(row)
            edge_str += '\n'
        return edge_str+'\n\n'
    
    def get_graph_str(self):
        graphs = []     # all graphs
        # get nodes and edges for each graph
        for key in self.init_struct['sets']:
            graph_set = self.init_struct['sets'][key]
            graph_nodes = graph_set['nodes']
            graph_edges = graph_set['edges']
            graphs.append({'nodes': graph_nodes, 'edges': graph_edges})

        graphs_str = ''
        for graph in graphs:
            graphs_str += '##graph\n@attribute\tcolor\n@type\tColor\n@default\t#ff807d8f\n\n#nodes\n@attribute\n@type\n@default\n'
            graphs_str += '\n'.join(graph['nodes']) # nodes
            graphs_str += '\n\n'
            graphs_str += '#edges\n@attribute\n@type\n@default\n' # edges
            graphs_str += '\n'.join(graph['edges']) # nodes
            graphs_str += '\n\n'
        
        return graphs_str


    def write_to_file(self):
        file_str = '#graph\n@attribute\n@type\n@default\n\n'
        nodes_str = self.get_nodes_str()
        edges_str = self.get_edges_str()
        graphs_str = self.get_graph_str()
        file_str += nodes_str + edges_str + graphs_str
        with open(self.pre_path+'/smooth.oco', 'w') as f:
            f.write(file_str)
    
    # write this file into a json file showing the relationship between setid and path id
    def write_set_path_dict_file(self):
        set_path_dict = {}
        for key in self.init_struct['sets']:
            set_path_dict[key] = self.init_struct['sets'][key]['edges']
        with open(self.pre_path+'/setPathDict.json', 'w') as f:
            json_object = json.dumps(set_path_dict, indent=4)
            f.write(json_object)