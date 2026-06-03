# exp1_black_hole_scaling.py
# Эксперимент 1: масштабирование задержки в топологической чёрной дыре.
# 
# Цель: изучить зависимость времени прохождения волны через область D (чёрную дыру)
# от размера D и уровня шума eta внутри дыры.
# 
# Параметры: N=20, D от 3 до 12, eta от 0.1 до 0.9, 30 симуляций на точку.
# Измеряется медианное время достижения вершины, следующей за дырой.
# 
# Результат: CSV-файл mg_scale_final.csv, сохраняется в /Preprint на Google Drive.

import sys
sys.path.append('.')
import numpy as np
import pandas as pd
import random
from utils import generate_gec_graph, measure_delay

# ---------- Подключение Google Drive ----------
from google.colab import drive
drive.mount('/content/drive')

# Создаём папку /Preprint в корне Drive
import os
preprint_dir = '/content/drive/MyDrive/Preprint'
os.makedirs(preprint_dir, exist_ok=True)
print(f"Результаты будут сохранены в {preprint_dir}")

# ---------- Параметры эксперимента ----------
N = 20
hole_sizes = range(3, 13)           # D: 3,4,...,12
eta_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
num_simulations = 30                # количество повторов для каждой (D, eta)
max_steps = 5000
num_runs_per_delay = 10             # количество прогонов волны для вычисления медианы

results = []

# ---------- Основной цикл ----------
for D in hole_sizes:
    for eta in eta_values:
        for sim in range(num_simulations):
            # Генерируем граф со средней степенью 4 (достаточно связный)
            G, order = generate_gec_graph(N, avg_deg=4, seed=sim*100 + D*10 + int(eta*100))
            
            # Навязываем глобальный гамильтонов цикл 0→1→2→...→N-1→0
            # (в реальной эмерджентной динамике он возник бы сам, здесь мы его фиксируем для чистоты эксперимента)
            for node in range(N):
                next_node = (node + 1) % N
                if next_node not in order[node]:
                    order[node].append(next_node)
                order[node].remove(next_node)
                order[node].insert(0, next_node)   # следующий по циклу – первый сосед
            
            # Стартовая вершина: последняя внутри дыры (если дыра начинается с 0)
            start = D-1 if D-1 >= 0 else 0
            # Целевая вершина: первая за пределами дыры
            target = D if D < N else N-1
            
            # Измеряем задержку
            delay = measure_delay(order, start, target, eta,
                                  max_steps=max_steps, num_runs=num_runs_per_delay)
            
            results.append({
                'D': D,
                'eta': eta,
                'sim': sim,
                'median_delay': delay if delay is not None else float('nan')
            })
            
            # Прогресс-индикатор
            print(f"D={D}, eta={eta}, sim={sim+1}/{num_simulations}, delay={delay}")

# ---------- Сохранение результатов ----------
df = pd.DataFrame(results)
output_path = os.path.join(preprint_dir, 'mg_scale_final.csv')
df.to_csv(output_path, index=False)
print(f"\nЭксперимент 1 завершён. Результаты сохранены в {output_path}")
