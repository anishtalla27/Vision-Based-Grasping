# Orientation ceiling for System A

System A can only output 0 or 90 degrees. For each test image this takes the labeled positive grasp whose angle is closest to one of those two orientations and reports how many images fall within each tolerance. The 30 degree row is the metric's own angle tolerance, so it is the hard ceiling: an image outside it cannot pass however well the rectangle is placed. Labels only, no predictions.

| Tolerance | Test images with a label within it | Share |
|---|---|---|
| 15 deg | 103/123 | 83.7% |
| 30 deg | 118/123 | 95.9% |

Images System A cannot pass at any placement (5): pcd0183, pcd0285, pcd0299, pcd0305, pcd0352

| Image | Nearest label angle to 0/90 (deg) |
|---|---|
| pcd0183 | 35.1 |
| pcd0285 | 30.1 |
| pcd0299 | 35.5 |
| pcd0305 | 31.9 |
| pcd0352 | 40.0 |
