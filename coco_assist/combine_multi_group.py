#!/usr/bin/env python
import os
import json
import argparse
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union, nearest_points
from tqdm import tqdm

def load_labelme_json(json_path):
    with open(json_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_labelme_json(data, json_path):
    with open(json_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def merge_polygons_with_connection(polygons, connection_width=1.0):
    """
    对一组多边形进行合并：
    1. 先使用 unary_union 得到初步合并结果；
    2. 若结果为 MultiPolygon，则采用简单 MST 算法，
       对各个不连通部分计算最近边界点对，
       用这些点生成细的连接线（buffer 后作为连接桥），
       再与原多边形一起 union。
    3. 如果 union 后依然为 MultiPolygon，则通过小幅 buffer(eps).buffer(-eps)
       强制合并为单一 Polygon（eps 取 connection_width/10）。
    """
    union_poly = unary_union(polygons)
    if union_poly.type == 'Polygon':
        return union_poly
    elif union_poly.type == 'MultiPolygon':
        poly_list = list(union_poly.geoms)
        n = len(poly_list)
        if n == 0:
            return None
        if n == 1:
            return poly_list[0]
        # 利用简单的 Prim 算法连接各个多边形
        connected = [0]
        edges = []
        not_connected = set(range(1, n))
        while not_connected:
            min_dist = float('inf')
            best_edge = None
            for i in connected:
                for j in not_connected:
                    d = poly_list[i].distance(poly_list[j])
                    if d < min_dist:
                        min_dist = d
                        best_edge = (i, j)
            if best_edge is None:
                break
            i, j = best_edge
            edges.append(best_edge)
            connected.append(j)
            not_connected.remove(j)
        # 根据 MST 边构造连接桥
        connection_polys = []
        for i, j in edges:
            p1, p2 = nearest_points(poly_list[i], poly_list[j])
            line = LineString([p1, p2])
            # 修改此处：将缓冲区由 connection_width/2.0 改为 connection_width/4.0，使连接桥更细
            connection_poly = line.buffer(connection_width / 4.0, cap_style=2)
            connection_polys.append(connection_poly)
        all_geoms = poly_list + connection_polys
        merged_poly = unary_union(all_geoms)
        # 若仍为 MultiPolygon，则尝试小幅 buffer 强制合并
        if merged_poly.type == 'MultiPolygon':
            eps = connection_width / 10.0
            merged_poly = merged_poly.buffer(eps).buffer(-eps)
        return merged_poly
    else:
        return union_poly

def process_labelme_json(json_data, connection_width=1.0):
    shapes = json_data.get("shapes", [])
    # 按 (label, group_id) 分组；如果某个 shape 没有 group_id，则 group_id 为 None
    groups = {}
    for shape in shapes:
        label = shape.get("label", "")
        group_id = shape.get("group_id", None)
        key = (label, group_id)
        groups.setdefault(key, []).append(shape)
    
    new_shapes = []
    for key, shape_list in groups.items():
        label, group_id = key
        if len(shape_list) > 1:
            # 多个 shape同时具有相同 label 和 group_id，执行合并
            polygons = []
            for shape in shape_list:
                pts = shape.get("points", [])
                if not pts:
                    continue
                # 确保多边形闭合
                if pts[0] != pts[-1]:
                    pts.append(pts[0])
                try:
                    poly = Polygon(pts)
                    if not poly.is_valid:
                        poly = poly.buffer(0)
                    polygons.append(poly)
                except Exception as e:
                    print(f"创建多边形出错 (label: {label}, group_id: {group_id}): {e}")
            if not polygons:
                continue
            merged_poly = merge_polygons_with_connection(polygons, connection_width)
            if merged_poly is None:
                continue
            # merged_poly 应该是单一 Polygon；取其外边界坐标
            try:
                exterior_coords = list(merged_poly.exterior.coords)
            except Exception as e:
                print(f"获取外边界出错 (label: {label}, group_id: {group_id}): {e}")
                continue
            new_shape = {
                "label": label,
                "points": exterior_coords,
                "shape_type": "polygon",
                "flags": {}
            }
            new_shapes.append(new_shape)
        else:
            # 只有一个 shape，则直接输出（去除 group_id）
            shape = shape_list[0]
            if "group_id" in shape:
                del shape["group_id"]
            new_shapes.append(shape)
    
    json_data["shapes"] = new_shapes
    return json_data

def process_folder(input_dir, output_dir, connection_width=1.0):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    json_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".json")]
    for filename in tqdm(json_files, desc="Processing JSON files"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        try:
            data = load_labelme_json(input_path)
            new_data = process_labelme_json(data, connection_width)
            save_labelme_json(new_data, output_path)
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="遍历文件夹中所有 labelme JSON 文件：当多个 polygon 同时具有相同 label 和 group_id 时合并，否则保持独立；输出时去除 group_id。"
    )
    parser.add_argument("input_dir", nargs='?', default="data", help="输入 JSON 文件所在的文件夹路径")
    parser.add_argument("output_dir", nargs='?', default="output", help="输出 JSON 文件存放的文件夹路径")
    parser.add_argument("--connection_width", type=float, default=1.0, help="连接部分的宽度（默认为 1.0）")
    args = parser.parse_args()
    
    process_folder(args.input_dir, args.output_dir, args.connection_width)
    print("全部处理完成！")

if __name__ == "__main__":
    main()
