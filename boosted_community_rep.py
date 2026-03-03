import argparse
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
import math
import xml.etree.ElementTree as ET
from networkx.algorithms import community as nx_comm
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--graphml', required=True)
    p.add_argument('--topk', type=int, default=15)
    p.add_argument('--yaml-out', default='focused_output.yaml', help='optional clang-uml YAML output path')
    p.add_argument('--no-namespaces', action='store_true', help='filter nodes typed as namespace in graphml parser')
    return p.parse_args()
def get_nodes_from_graphml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    keymap = {}
    for key in root.findall('.//g:key', ns):
        kid = key.get('id')
        an = key.get('attr.name')
        keymap[kid] = an
    node_names = {}   
    node_types = {}   
    def extract(graph_elem, ns_path=[]):
        for node in graph_elem.findall('g:node', ns):
            nid = node.get('id')
            name = None
            ntype = None
            for data in node.findall('g:data', ns):
                k = data.get('key')
                attr = keymap.get(k)
                val = data.text.strip() if data.text else None
                if not val: continue
                if attr in ('name','display_name'):
                    name = val
                elif attr == 'type':
                    ntype = val
            if name:
                if ntype == 'namespace':
                    q = '::'.join(ns_path + [name]) if ns_path else name
                    node_names[nid] = q
                    node_types[nid] = 'namespace'
                    new_ns = ns_path + [name]
                else:
                    q = ('::'.join(ns_path) + '::' + name) if ns_path else name
                    node_names[nid] = q
                    node_types[nid] = ntype or 'type'
                    new_ns = ns_path
            else:
                new_ns = ns_path
                if ntype:
                    node_types[nid] = ntype
            nested = node.find('g:graph', ns)
            if nested is not None:
                extract(nested, new_ns)
    rg = root.find('.//g:graph', ns)
    if rg is not None:
        extract(rg, [])
    return node_names, node_types
def read_graph(graphml_path):
    G = nx.read_graphml(graphml_path)
    node_names, node_types = get_nodes_from_graphml(graphml_path)
    return G, node_names, node_types
def neighbor_h_index(G, node):
    degs = sorted([G.degree(n) for n in G.neighbors(node)], reverse=True)
    h = 0
    for i, d in enumerate(degs, start=1):
        if d >= i:
            h = i
        else:
            break
    return h
def manifold_ranking_score(G, prior=None, alpha=0.99, max_iter=200, tol=1e-6):
    nodes = list(G.nodes())
    n = len(nodes)
    idx = {v:i for i,v in enumerate(nodes)}
    A = nx.to_numpy_array(G, nodelist=nodes, weight=None)
    deg = A.sum(axis=1)
    D_inv_sqrt = np.zeros_like(A)
    for i in range(n):
        if deg[i] > 0:
            D_inv_sqrt[i,i] = 1.0/math.sqrt(deg[i])
    S = D_inv_sqrt.dot(A).dot(D_inv_sqrt)
    if prior is None:
        y = np.ones(n) / n
    else:
        y = np.array([prior.get(v,0.0) for v in nodes], dtype=float)
        if y.sum() == 0:
            y = np.ones(n)/n
        else:
            y = y / y.sum()
    f = y.copy()
    for t in range(max_iter):
        f_next = alpha * S.dot(f) + (1.0-alpha)*y
        if np.linalg.norm(f_next - f) < tol:
            f = f_next
            break
        f = f_next
    return {nodes[i]: float(f[i]) for i in range(n)}
def normalize_map(d):
    if not d: return d
    vals = np.array(list(d.values()), dtype=float)
    mn, mx = vals.min(), vals.max()
    if mx == mn:
        return {k: 0.0 for k in d}
    return {k: float((v-mn)/(mx-mn)) for k,v in d.items()}
def compute_all_metrics(G, node_names, node_types, no_namespaces=False):
    G = G.copy()
    selfloops = list(nx.selfloop_edges(G))
    if selfloops:
        print(f"[info] Removing {len(selfloops)} self-loop edges (examples): {selfloops[:5]}")
        G.remove_edges_from(selfloops)
    if G.is_multigraph():
        print("[info] Collapsing multigraph to simple graph (merging parallel edges).")
        simple = nx.DiGraph() if G.is_directed() else nx.Graph()
        simple.add_nodes_from(G.nodes(data=True))
        for u, v in G.edges():
            simple.add_edge(u, v)
        G = simple
    G_undirected = G.to_undirected()
    deg = dict(G.degree())
    deg_cent = nx.degree_centrality(G) if G.number_of_nodes() > 0 else {n: 0.0 for n in G.nodes()}
    print("CENTRALITY")
    for u,v in deg_cent.items():
        print(u,v)
    if G.number_of_nodes() > 0 and G.number_of_edges() > 0:
        if G.is_directed():
            pagerank = nx.pagerank(G)
        else:
            pagerank = nx.pagerank(G_undirected)
    else:
        pagerank = {n: 1.0 / max(1, G.number_of_nodes()) for n in G.nodes()}
    betw = nx.betweenness_centrality(G_undirected, normalized=True) if G.number_of_edges() > 0 else {n: 0.0 for n in G.nodes()}
    if G_undirected.number_of_nodes() == 0:
        eig = {n: 0.0 for n in G.nodes()}
    else:
        try:
            eig = nx.eigenvector_centrality(G_undirected, max_iter=1000)
        except:
            eig = {}
            for component in nx.connected_components(G_undirected):
                subgraph = G_undirected.subgraph(component).copy()
                component_eig = nx.eigenvector_centrality(subgraph, max_iter=1000)
                eig.update(component_eig)
            for n in G.nodes():
                if n not in eig:
                    eig[n] = 0.0
    clos = nx.closeness_centrality(G_undirected)
    core = nx.core_number(G_undirected) if G_undirected.number_of_nodes() > 0 else {n: 0 for n in G.nodes()}
    def neighbor_h_index_local(G_local, node):
        degs = sorted([G_local.degree(nb) for nb in G_local.neighbors(node)], reverse=True)
        h = 0
        for i, d in enumerate(degs, start=1):
            if d >= i:
                h = i
            else:
                break
        return h
    h_idx = {n: neighbor_h_index_local(G_undirected, n) for n in G.nodes()}
    art_set = set(nx.articulation_points(G_undirected))
    artic = {n: (1 if n in art_set else 0) for n in G.nodes()}
    mr_prior = {n: deg_cent.get(n, 0.0) for n in G.nodes()}
    mr_score = manifold_ranking_score(G_undirected, prior=mr_prior)
    nd = normalize_map(deg_cent)
    npg = normalize_map(pagerank)
    nb = normalize_map(betw)
    ne = normalize_map(eig)
    nc = normalize_map(clos)
    nk = normalize_map(core)
    nh = normalize_map(h_idx)
    nm = normalize_map(mr_score)
    combined = {}
    for n in G.nodes():
        combined[n] = (nd.get(n,0)*0.15 + npg.get(n,0)*0.30 + nb.get(n,0)*0.25 +
                       nk.get(n,0)*0.15 + nm.get(n,0)*0.15)
    rows = []
    for n in G.nodes():
        if no_namespaces and node_types.get(n)=='namespace':
            continue
        rows.append({
            'id': n,
            'name': node_names.get(n, n),
            'degree': int(deg.get(n,0)),
            'deg_cent': float(deg_cent.get(n,0)),
            'pagerank': float(pagerank.get(n,0)),
            'betweenness': float(betw.get(n,0)),
            'eigenvector': float(eig.get(n,0)),
            'closeness': float(clos.get(n,0)),
            'core': int(core.get(n,0)),
            'h_index_neighbors': int(h_idx.get(n,0)),
            'articulation': int(artic.get(n,0)),
            'manifold': float(mr_score.get(n,0)),
            'combined': float(combined.get(n,0))
        })
    import pandas as pd
    df = pd.DataFrame(rows)
    df = df.sort_values('combined', ascending=False)
    return df
def get_score_map(df, strategy, custom_metrics=None, weights=None):
    def _minmax(arr):
        arr = np.array(arr, dtype=float)
        mn = np.nanmin(arr)
        mx = np.nanmax(arr)
        if np.isnan(mn) or np.isnan(mx) or mx == mn:
            return np.zeros_like(arr, dtype=float)
        return (arr - mn) / (mx - mn)
    centrality_metrics = ['deg_cent', 'pagerank', 'betweenness', 'eigenvector', 'closeness']
    structural_metrics = ['core', 'h_index_neighbors', 'articulation', 'manifold']
    all_metrics = centrality_metrics + [m for m in structural_metrics]
    strategy = strategy.lower()
    if strategy == 'all':
        metrics = [m for m in all_metrics if m in df.columns]
    elif strategy == 'centrality':
        metrics = [m for m in centrality_metrics if m in df.columns]
    elif strategy == 'structural':
        metrics = [m for m in structural_metrics if m in df.columns]
    elif strategy == 'combined':
        scores = _minmax(df['combined'].values)
        return dict(zip(df['id'].values, scores.astype(float)))
    elif strategy == 'rank':
        metrics = [m for m in centrality_metrics]
        ranks = np.zeros((len(df), len(metrics)), dtype=float)
        for i, m in enumerate(metrics):
            ranks[:, i] = df[m].rank(method='average', ascending=False).values
        avg_ranks = np.nanmean(ranks, axis=1)
        inv = np.max(avg_ranks) - avg_ranks
        scores = _minmax(inv)
        return dict(zip(df['id'].values, scores.astype(float)))
    else:
        raise ValueError(f"Unknown strategy '{strategy}'. Supported: all, centrality, structural, combined, rank, custom")
    if not metrics:
        return dict(zip(df['id'].values, np.zeros(len(df), dtype=float)))
    norm_cols = []
    for m in metrics:
        col = df[m].values if m in df.columns else np.full(len(df), np.nan)
        norm_cols.append(_minmax(col))
    mat = np.vstack(norm_cols).T  
    if weights is None:
        w = np.ones(mat.shape[1], dtype=float) / mat.shape[1]
    else:
        w = np.array(weights, dtype=float)
        if w.size != mat.shape[1]:
            raise ValueError("weights length must equal number of metrics")
        if w.sum() == 0:
            raise ValueError("weights must not sum to zero")
        w = w / w.sum()
    scores = mat.dot(w)
    scores = np.clip(scores, 0.0, 1.0)
    return dict(zip(df['id'].values, scores.astype(float)))
def write_yaml_for_clanguml(selected_names, out_path):
    lines = []
    lines.append("compilation_database_dir: build")
    lines.append("output_directory: docs/diagrams")
    lines.append("diagrams:")
    lines.append("  selected_auto:")
    lines.append("    type: class")
    lines.append("    generate_packages: true")
    lines.append("    include:")
    lines.append("      elements:")
    for s in selected_names:
        lines.append(f'      - "{s}"')
    Path(out_path).write_text("\n".join(lines))
    print(f"Wrote YAML to {out_path}")
def is_namespace_node(n, node_types):
    return node_types.get(n) == 'namespace'
def boosted_community_rep(G, node_names, node_types, score_map, topk, per_community=1, filter_ns=False):
    und = G.to_undirected() if G.is_directed() else G
    communities = list(nx_comm.greedy_modularity_communities(und))
    for idx, comm in enumerate(communities):
        print(f"\n--- Community {idx} ---")
        for n in comm:
            print(f"{n}: {node_names.get(n, '?')}")
    comm_scores = []
    for c in communities:
        score = sum(score_map.get(n,0) for n in c)
        comm_scores.append((score, c))
    comm_scores.sort(key=lambda x: x[0], reverse=True)
    selected = []
    for score, comm in comm_scores:
        members = sorted(list(comm), key=lambda n: score_map.get(n,0), reverse=True)
        picked = 0
        for m in members:
            if filter_ns and is_namespace_node(m, node_types,):
                continue
            selected.append(m)
            picked += 1
            if picked >= per_community:
                break
        if len(selected) >= topk:
            break
    if len(selected) < topk:
        filler = [n for n,_ in sorted(score_map.items(), key=lambda kv: kv[1], reverse=True)]
        for f in filler:
            if f not in selected:
                if filter_ns and is_namespace_node(f, node_types):
                    continue
                selected.append(f)
            if len(selected) >= topk:
                break
    return selected[:topk]
def readable_name(n, node_names_dict, G):
    if n in node_names_dict:
        return node_names_dict[n]
    attrs = G.nodes.get(n, {})
    return attrs.get('name') or attrs.get('display_name') or attrs.get('label') or str(n)
def main():
    args = parse_args()
    G, node_names, node_types = read_graph(args.graphml)
    all_node_ids = set(node_names.keys()) | set(G.nodes())
    for nid in all_node_ids:
        if nid not in G:
            G.add_node(nid)
    df = compute_all_metrics(G, node_names, node_types, no_namespaces=args.no_namespaces)
    out = Path('metrics.csv')
    df.to_csv(out, index=False)
    print(f"Wrote metrics to {out}")
    sm=get_score_map(df,'all')
    sel = boosted_community_rep(G, node_names, node_types, sm, topk=args.topk, per_community=2, filter_ns=args.no_namespaces)
    print("------------------------")
    print(sel)
    selected_names = [readable_name(n, node_names, G) for n in sel]
    if args.yaml_out:
        sel = selected_names
        write_yaml_for_clanguml(sel, args.yaml_out)
if __name__ == '__main__':
    main()
