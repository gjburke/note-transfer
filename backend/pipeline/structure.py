import numpy as np
from sklearn.cluster import DBSCAN
from anytree import Node
from collections import namedtuple

# Assuming already sorted
def gap_cluster(x, gap):
    labels = np.zeros(len(x), dtype=int)
    cluster = 0

    for i in range(1, len(x)):
        if x[i] - x[i-1] > gap:
            cluster += 1
        labels[i] = cluster

    return labels

# Finds pairs in already sorted values, helps with matching bullet and text
def find_pairs(values):
    if len(values) < 2:
        return [0]

    diffs = np.diff(values)
    if len(diffs) > 1:
        lower, upper = diffs.mean() - 2*diffs.std(), diffs.mean() + 2*diffs.std()
        diffs = diffs[(diffs > lower) & (diffs < upper)]
    gap = (diffs.min() + diffs.max())/2

    values = values.reshape((-1, 1))
    labels = gap_cluster(values, gap)
    return labels

def find_clusters(values):
    if len(values) < 2:
        return [0]

    diffs = np.diff(sorted(values))
    if len(diffs) > 1:
        lower, upper = diffs.mean() - 2*diffs.std(), diffs.mean() + 2*diffs.std()
        diffs = diffs[(diffs > lower) & (diffs < upper)]
    else:
        return [0,0]
    gap = (diffs.min() + diffs.max())/2

    values = values.reshape((-1, 1))
    labels = DBSCAN(eps=gap, min_samples=1).fit_predict(values)
    return labels

# For parsing, will have to figure out class labels and ids, for now its:

# large-sections

# 0. Header
# 1. Section

# by-line

# 0. Nothing/Undefined 
# 1. Unordered Bullet
# 2. Ordered Bullet
# 3. Text
# 4. Figure

Entry = namedtuple('Entry', ['node', 'level'])

def is_bullet(node):
    return node.cls_id == 1 or node.cls_id == 2

def is_text(node):
    return node.cls_id == 3

def parse_section(parent, nodes):
    y_values = np.array([node.y for node in nodes])
    vertical_labels = find_pairs(y_values)

    x_values = np.array([node.x for node in nodes])
    text_xs = np.array([[node.x, i] for i, node in enumerate(nodes) if is_text(node)])
    if len(text_xs) == 0:
        return
    horizontal_text_labels = find_clusters(text_xs[:, 0])

    horizontal_labels = np.zeros(len(nodes))
    horizontal_labels[text_xs[:, 1].astype(int)] = horizontal_text_labels

    parents = [Entry(parent, -1)]

    for i in range(len(nodes)):
        if i != len(nodes)-1 and vertical_labels[i] == vertical_labels[i+1]:
            horizontal_labels[i] = max(horizontal_labels[i], horizontal_labels[i+1])
            horizontal_labels[i+1] = max(horizontal_labels[i], horizontal_labels[i+1])

        # Flip bullet and text if text comes first
        if (i != len(nodes)-1 and 
            is_text(nodes[i]) and 
            is_bullet(nodes[i+1]) and
            vertical_labels[i] == vertical_labels[i+1]):

            temp = nodes[i]
            nodes[i] = nodes[i+1]
            nodes[i+1] = temp

        node = nodes[i]
        if is_text(node):
            while (horizontal_labels[i] < parents[-1].level):
                parents.pop()
            node.parent = parents[-1].node
        else:   
            while (horizontal_labels[i] <= parents[-1].level):
                parents.pop()
            node.parent = parents[-1].node

        if is_bullet(node):
            parents.append(Entry(node, horizontal_labels[i]))

def get_average_angle(nodes):
    sum_r = 0
    for node in nodes:
        sum_r += node.r
    avg_r = sum_r / len(nodes) 
    return avg_r

def correct_node_corners(nodes, center):
    x_values = [node.x for node in nodes]
    y_values = [node.y for node in nodes]

    xy = np.array([x_values, y_values]).T
    angle = get_average_angle(nodes)
    rot = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])

    return (xy - center) @ rot.T + center

def get_root():
    return Node("Root", cls_id=-1, is_section=True)

def parse_page(root, nodes, width, height):
    sections = [node for node in nodes if node.is_section]
    indices = [i for i in range(len(nodes)) if nodes[i].is_section] + [len(nodes)]

    xy = correct_node_corners(sections,  (width/2, height/2))
    levels = find_clusters(xy[:, 0])
    
    parents = [Entry(root, -1)]
    for i, (node, level, index) in enumerate(zip(sections, levels, indices)):
        while level <= parents[-1].level:
            parents.pop()
        
        node.parent = parents[-1].node
        parents.append(Entry(node, level))

        parse_section(node, nodes[index+1:indices[i+1]])