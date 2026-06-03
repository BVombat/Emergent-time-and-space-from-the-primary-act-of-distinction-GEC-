# exp2_hierarchical_bh.py
# Эксперимент 2: иерархические чёрные дыры (внешняя + внутренняя).
# 
# Цель: исследовать влияние вложенности и инверсии порядка внутри дыр на вероятность выхода волны.
# 
# Параметры:
#   D1 – размер внешней дыры, D2 – внутренней,
#   shift – смещение внутренней дыры относительно внешней,
#   eta – уровень шума,
#   inv_outer/inv_inner – инверсия порядка соседей в дыре.
# 
# Измеряется escape_prob – доля успешных достижений вершины N-1 из 0 за max_steps.
# Результат: hier_final.csv в /Preprint.

import sys
sys.path.append('.')
import numpy as np
import pandas as pd
import random
from utils import generate_gec_graph, measure_delay

# Подключение Drive
from google.colab import drive
drive.mount('/content/drive')
preprint_dir = '/content/drive/MyDrive/Preprint'
os.makedirs(preprint_dir, exist_ok=True)
print(f"Результаты будут сохранены в {preprint_dir}")

# Параметры
N = 30
D1_vals = [3, 5, 7, 10]
D2_vals = [2, 4, 6]
shift_vals = [0, 1, 2, 3]
eta_vals = [0.2, 0.5, 0.8]
inv_outer_vals = [False, True]
inv_inner_vals = [False, True]
num_sims = 20                # количество графов на точку
max_steps = 2000
trials_per_sim = 30          # число попыток волны для оценки вероятности

results = []

for D1 in D1_vals:
    for D2 in D2_vals:
        if D1 + D2 > N-2:    # чтобы дыры не вылезали за пределы
            continue
        for shift in shift_vals:
            for eta in eta_vals:
                for inv_outer in inv_outer_vals:
                    for inv_inner in inv_inner_vals:
                        for sim in range(num_sims):
                            seed = sim*1000 + D1*100 + D2*10 + shift
                            G, order = generate_gec_graph(N, avg_deg=4.5, seed=seed)
                            
                            # Определяем дыры
                            outer_hole = set(range(D1))
                            inner_start = D1 + shift
                            inner_hole = set(range(inner_start, inner_start + D2))
                            
                            # Инверсия порядка (разворот списка соседей, кроме первого)
                            if inv_outer:
                                for node in outer_hole:
                                    if len(order[node]) > 1:
                                        order[node] = [order[node][0]] + list(reversed(order[node][1:]))
                            if inv_inner:
                                for node in inner_hole:
                                    if len(order[node]) > 1:
                                        order[node] = [order[node][0]] + list(reversed(order[node][1:]))
                            
                            # Оценка вероятности выхода из 0 в N-1
                            success = 0
                            for _ in range(trials_per_sim):
                                steps = measure_delay(order, 0, N-1, eta,
                                                      max_steps=max_steps, num_runs=1)
                                if steps is not None:
                                    success += 1
                            escape_prob = success / trials_per_sim
                            
                            results.append({
                                'D1': D1, 'D2': D2, 'shift': shift, 'eta': eta,
                                'inv_outer': inv_outer, 'inv_inner': inv_inner,
                                'escape_prob': escape_prob
                            })
                            print(f"D1={D1} D2={D2} shift={shift} eta={eta} inv_o={inv_outer} inv_i={inv_inner} sim={sim+1}/{num_sims} -> prob={escape_prob:.2f}")

df = pd.DataFrame(results)
output_path = os.path.join(preprint_dir, 'hier_final.csv')
df.to_csv(output_path, index=False)
print(f"\nЭксперимент 2 завершён. Сохранено в {output_path}")