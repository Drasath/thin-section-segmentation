from skimage import io, color
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import cv2
import time

PROJECT_DIRECTORY = Path(__file__).resolve().parents[2]
GROUND_TRUTH = Path(PROJECT_DIRECTORY / 'resources' / 'images' / 'goal.tif')
MAX_ITERATIONS = 100
rank = 0

def jaccard_distance(segmentation, ground_truth):
    intersection = np.logical_and(segmentation, ground_truth)
    union = np.logical_or(segmentation, ground_truth)
    return 1 - intersection.sum() / union.sum()

def dice_coefficient(segmentation, ground_truth):
    intersection = np.logical_and(segmentation, ground_truth)
    return 2 * intersection.sum() / (segmentation.sum() + ground_truth.sum())

def boolean_dice_sorensen_coefficient(segmentation, ground_truth):
    true_positive = np.logical_and(segmentation, ground_truth).sum()
    false_positive = np.logical_and(segmentation, np.logical_not(ground_truth)).sum()
    false_negative = np.logical_and(np.logical_not(segmentation), ground_truth).sum()
    return (2*true_positive) / ((2*true_positive) + false_positive + false_negative)

def merge_independent_score(segmentation, ground_truth):
    # For each segment in the result, compare with the ground truth (i.e. Check if the segment is in a ground truth segment, and if it is in multiple segments, intersect with the closest segment and subtract that from the size of the segment, then divide by the size of the segment)
    
    intersection = np.logical_and(segmentation, ground_truth)
    return (intersection.sum() / segmentation.sum())

if __name__ == '__main__':
    # Load the ground truth image
    ground_truth = io.imread(GROUND_TRUTH, plugin='pil')
    ground_truth = cv2.cvtColor(ground_truth, cv2.COLOR_BGR2HSV)
    
    # threshold = 0
    # ground_truth[:, :, 1] = (ground_truth[:, :, 1] > threshold) * 255
    # ground_truth_background = ground_truth[:, :, 0] == 0
    # ground_truth[:, :, 2] = 255
    # ground_truth[ground_truth_background] = 0

    ground_truth = cv2.cvtColor(ground_truth, cv2.COLOR_HSV2RGB)

    segmentation = np.load(Path(PROJECT_DIRECTORY / 'saves' / '62_subject100.save'))
    segmentation = cv2.resize(segmentation, (ground_truth.shape[1], ground_truth.shape[0]), interpolation=cv2.INTER_NEAREST)

    total_score = 0
    iterations = 0
    for segment in np.unique(ground_truth[:, :, 0]):
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

if __name__ == '__main__':
    # Shared variables
    total_score = 0
    iterations = 0

    # Load the ground truth image
    ground_truth = io.imread(GROUND_TRUTH, plugin='pil')

    # Load the segmentation result
    segmentation = np.load(Path(PROJECT_DIRECTORY / 'saves' / '62_subject100.save'))
    segmentation = cv2.resize(segmentation, (ground_truth.shape[1], ground_truth.shape[0]), interpolation=cv2.INTER_NEAREST)

    # MPI Implementation
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
