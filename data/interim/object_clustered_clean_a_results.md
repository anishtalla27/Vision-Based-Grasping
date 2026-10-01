Clean System A (frozen table, afcd99a): 50/123 = 40.7%
  correct         50 (40.7)
  angle_only      15 (12.2)
  iou_only        16 (13.0)
  both            34 (27.6)
  no_prediction    8 ( 6.5)
  center outside labelled-grasp hull: 28/115 (24.3%)

Test images with a labelled grasp within 15 deg of 0/90: 103/123 (83.7%)
Test images with a labelled grasp within 30 deg of 0/90: 118/123 (95.9%)

objects: 35  bootstrap 20000, permutation 20000, seed 0

Object-clustered 95% CIs (image-level accuracy)
  A          57.7%   [ 46.2,  68.2]
  B          79.7%   [ 70.8,  87.1]
  C_pooled   12.4%   [  8.0,  17.4]
  C_best5    35.0%   [ 24.6,  45.5]
  A_clean    40.7%   [ 28.0,  53.2]
  B_v2       84.0%   [ 73.9,  92.1]
  D_geom     55.3%   [ 41.8,  68.0]

Object-balanced accuracy
  A          51.3%   [ 40.0,  62.4]
  B          75.4%   [ 64.5,  85.1]
  C_pooled   10.5%   [  7.0,  14.3]
  C_best5    29.8%   [ 21.1,  38.5]
  A_clean    38.5%   [ 27.2,  50.3]
  B_v2       79.8%   [ 68.9,  89.4]
  D_geom     50.3%   [ 37.1,  63.4]

Paired differences (object-clustered bootstrap CI, permutation p)
  B         - A_clean    +39.0   [ +25.2,  +52.9]  excludes 0   p = 5e-05
  B_v2      - A_clean    +43.4   [ +29.9,  +56.7]  excludes 0   p = 5e-05
  A_clean   - C_best5     +5.7   [  -6.1,  +18.0]  INCLUDES 0   p = 0.4544
  A_clean   - C_pooled   +28.3   [ +16.9,  +40.0]  excludes 0   p = 0.0001
  D_geom    - A_clean    +14.6   [  +4.7,  +24.8]  excludes 0   p = 0.01505
  A         - A_clean    +17.1   [  +8.6,  +25.8]  excludes 0   p = 0.0022
