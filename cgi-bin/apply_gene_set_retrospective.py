#!/usr/bin/env python
#========================================================================================#
import numpy as np, sys, h5py, json

base_dir = sys.argv[1]
sub_dirs = sys.argv[2]
gene_sets_path = sys.argv[3]

# Load gene sets
gene_sets = {}
all_genes = set([])
for l in open(gene_sets_path).read().split('\n'):
	l = l.split('\t')
	gene = l[0]
	name = l[1]
	if not name in gene_sets:
		gene_sets[name] = []
	gene_sets[name].append(gene)
	all_genes.add(gene)


# Load gene expression 
gene_exp = {}
hf = h5py.File(base_dir + '/counts_norm_sparse_genes.hdf5', 'r')
ncells = hf.attrs['ncells']
for g in all_genes:
	ee = np.zeros(ncells)
	counts = np.array(hf.get('counts').get(g))
	cell_ix = np.array(hf.get('cell_ix').get(g))
	ee[cell_ix] = counts
	gene_exp[g] = ee

# compute scores
scores = {}
for k,gs in gene_sets.items():
	Z = np.array([gene_exp[g] for g in gs])
	Z = (Z - np.mean(Z,axis=1)[:,None]) / np.std(Z,axis=1)[:,None]
	ss = np.sum(Z,axis=0)
	ss = ss - np.min(ss)
	scores[k] = ss

# Apply to each subplots
for dd in sub_dirs.split(','):
	cell_ix = np.load(base_dir+'/'+dd+'/cell_filter.npy')
	f = open(base_dir+'/'+dd+'/color_data_gene_sets.csv','a')
	for k,ss in scores.items():
		newline = ','.join([k]+[repr(x) for x in ss[cell_ix]])
		print dd, newline
		f.write(newline+'\n')
	f.close()
	
	color_stats = json.load(open(base_dir+'/'+dd+'/color_stats.json'))
	for k,ss in scores.items(): 
		color_stats[k] = (np.mean(ss),np.std(ss),np.min(ss),np.max(ss),np.percentile(ss,99))
	json.dump(color_stats,open(base_dir+'/'+dd+'/color_stats.json','w'))



