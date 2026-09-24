objects: 35   images: 123
bootstrap: 20000 resamples, permutation: 20000, seed 0

Object-clustered 95% CIs (image-level accuracy)
  A          57.7%   [ 46.2,  68.2]
  B          79.7%   [ 70.8,  87.1]
  C_pooled   12.4%   [  8.0,  17.4]
  C_best5    35.0%   [ 24.6,  45.5]

Object-balanced accuracy (each object weighted equally)
  A          51.3%   [ 40.0,  62.4]
  B          75.4%   [ 64.5,  85.1]
  C_pooled   10.5%   [  7.0,  14.3]
  C_best5    29.8%   [ 21.1,  38.5]

Paired differences (object-clustered bootstrap CI, permutation p)
  B         - A          +22.0   [  +9.7,  +35.1]  excludes 0   p = 0.0031
  A         - C_best5    +22.8   [  +9.2,  +35.6]  excludes 0   p = 0.00595
  A         - C_pooled   +45.4   [ +33.8,  +55.6]  excludes 0   p = 5e-05
  B         - C_pooled   +67.3   [ +58.1,  +75.8]  excludes 0   p = 5e-05

Overlap check on the paper's original claim
  System A lower bound      : 46.2
  System C best-of-5 upper  : 45.5
  gap                       : +0.7
