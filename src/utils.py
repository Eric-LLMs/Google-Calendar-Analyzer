# src/utils.py
import datetime


def solve_overlaps(df_subset):
    """
    贪心算法：为重叠事件分配子轨道 (Sub-lanes)。
    返回: (assignments, max_lanes)
    """
    df_subset = df_subset.sort_values('Local Start')
    lanes = []
    assignments = []

    for _, row in df_subset.iterrows():
        start = row['Local Start']
        placed = False
        for i, end_time in enumerate(lanes):
            # 5分钟缓冲，避免视觉粘连
            if start >= (end_time - datetime.timedelta(minutes=5)):
                lanes[i] = row['Local End']
                assignments.append(i)
                placed = True
                break
        if not placed:
            lanes.append(row['Local End'])
            assignments.append(len(lanes) - 1)

    return assignments, len(lanes)