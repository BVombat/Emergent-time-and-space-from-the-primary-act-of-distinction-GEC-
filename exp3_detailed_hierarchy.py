# exp3_detailed_hierarchy.py
# Эксперимент 3: детальное сканирование параметров иерархических чёрных дыр.
# 
# Цель: выявить резонансные эффекты и критическую роль положения внутренней дыры (shift)
# и доли инвертированных вершин (inv_ratio) внутри неё.
# 
# Параметры:
#   D2 – размер внутренней дыры,
#   shift – смещение,
#   inv_ratio – доля вершин внутренней дыры с инвертированным порядком.
# 
# Измеряется медианная задержка прохождения от входа во внешнюю дыру до выхода из внутренней.
# Результат: detailed_final.csv в /Preprint.

import sys
sys.path.append('.')
import numpy as np
import pandas as pd
import random
from utils import generate_gec_graph, measure_delay

from google.colab import drive
drive.mount('/content/drive')
import os
preprint_dir = '/content/drive/MyDrive/Preprint'
os.makedirs(preprint_dir, exist_ok=True)
print(f"Результаты будут сохранены в {preprint_dir}")

# Параметры
N = 30
D1 = 5                     # фиксированный размер внешней дыры
D2_vals = [2, 3, 4, 5]
shift_vals = [0, 1, 2]
eta = 0.5                  # фиксированный шум
inv_ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
num_sims = 20
max_steps = 2000
num_runs_per_delay = 30

results = []

for D2 in D2_vals:
    for shift in shift_vals:
        for inv_ratio in inv_ratios:
            for sim in range(num_sims):
                seed = sim*1000 + D2*100 + shift*10 + int(inv_ratio*100)
                G, order = generate_gec_graph(N, avg_deg=4.5, seed=seed)
                
                outer_hole = set(range(D1))
                inner_start = D1 + shift
                inner_hole = list(range(inner_start, inner_start + D2))
                
                # Инвертируем inv_ratio долю вершин внутренней дыры
                num_inv = int(len(inner_hole) * inv_ratio)
                inv_nodes = random.sample(inner_hole, num_inv)
                for node in inv_nodes:
                    if len(order[node]) > 1:
                        order[node] = [order[node][0]] + list(reversed(order[node][1:]))
                
                # Старт: последняя вершина внешней дыры (вход), цель: первая после внутренней дыры
                start = D1 - 1
                target = inner_start + D2
                if target >= N:
                    target = N-1
                
                delay = measure_delay(order, start, target, eta,
                                      max_steps=max_steps, num_runs=num_runs_per_delay)
                
                results.append({
                    'D2': D2, 'shift': shift, 'inv_ratio': inv_ratio,
                    'sim': sim, 'median_delay': delay if delay is not None else float('nan')
                })
                print(f"D2={D2} shift={shift} inv_ratio={inv_ratio} sim={sim+1}/{num_sims} delay={delay}")

df = pd.DataFrame(results)
output_path = os.path.join(preprint_dir, 'detailed_final.csv')
df.to_csv(output_path, index=False)
print(f"\nЭксперимент 3 завершён. Сохранено в {output_path}")