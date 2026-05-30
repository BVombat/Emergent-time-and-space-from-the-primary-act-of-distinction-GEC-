# utils.py
import numpy as np
import random
import networkx as nx

def generate_gec_graph(N, avg_deg, seed=None):
    """Генерация связного графа и случайного порядка соседей."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    p = avg_deg / (N-1)
    G = nx.fast_gnp_random_graph(N, p, seed=seed)
    # Обеспечиваем связность
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(len(components)-1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i+1]))
            G.add_edge(u, v)
    # Случайный циклический порядок соседей для каждой вершины
    order = {}
    for node in G.nodes():
        neigh = list(G.neighbors(node))
        random.shuffle(neigh)
        order[node] = neigh
    return G, order

def propagate_wave(order, start, target, eta, max_steps):
    """Распространение волны: на каждом шаге с вероятностью eta – случайный сосед, иначе первый."""
    steps = 0
    current = start
    while current != target and steps < max_steps:
        if random.random() < eta:
            nxt = random.choice(order[current])
        else:
            nxt = order[current][0]
        current = nxt
        steps += 1
    return steps if steps < max_steps else None

def measure_delay(order, start, target, eta, max_steps=1000, num_runs=100):
    """Медианное время достижения target из start с шумом eta."""
    delays = []
    for _ in range(num_runs):
        steps = propagate_wave(order, start, target, eta, max_steps)
        if steps is not None:
            delays.append(steps)
    if not delays:
        return None
    return np.median(delays)