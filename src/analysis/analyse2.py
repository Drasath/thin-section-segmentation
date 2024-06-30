from mpi4py import MPI
import numpy as np
import cv2
from skimage import io, color
from pathlib import Path
import matplotlib.pyplot as plt

PROJECT_DIRECTORY = Path(__file__).resolve().parents[2]
GROUND_TRUTH = Path(PROJECT_DIRECTORY / 'resources' / 'images' / 'goal.tif')
MAX_ITERATIONS = 40

def jaccard_distance(segmentation, ground_truth):
    intersection = np.logical_and(segmentation, ground_truth)
    union = np.logical_or(segmentation, ground_truth)
    return 1 - intersection.sum() / union.sum()

if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Shared variables
    ground_truth = io.imread(GROUND_TRUTH, plugin='pil')

    segmentation = np.load(Path(PROJECT_DIRECTORY / 'saves' / '62_subject100.save'))
    segmentation = cv2.resize(segmentation, (ground_truth.shape[1], ground_truth.shape[0]), interpolation=cv2.INTER_NEAREST)

    total_score = 0
    iterations = 0
    ground_truth_segments = np.unique(ground_truth[:, :, 0])
    begin = rank * len(ground_truth_segments) // size
    end = (rank + 1) * len(ground_truth_segments) // size
    for segment in ground_truth_segments[begin::end]:
        segment_mask = ground_truth[:, :, 0] == segment
        best_score = 1
        best_segment = None
        iterations += 1
        for result_segment in np.unique(segmentation):
            result_segment_mask = segmentation == result_segment
            score = jaccard_distance(result_segment_mask, segment_mask)
            if score < best_score:
                best_score = score
                best_segment = result_segment
        total_score += 1 - best_score
        # if best_segment is not None:
        #     plt.imshow(segmentation == best_segment, cmap='Greens_r')
        #     plt.imshow(segment_mask, alpha=0.5, cmap='Reds_r')
        #     plt.show()
        

        if iterations == MAX_ITERATIONS:
            break
        
    print(total_score / iterations)