import time
from mpi4py import MPI
from pathlib import Path
from skimage import io, color
import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage import segmentation
from skimage.measure import regionprops

PROJECT_DIRECTORY = Path(__file__).resolve().parents[2]
MAX_SEGMENTS = 200000
MIN_SEGMENT_SIZE = 100


def start_timer():
    print("Starting analysis")
    global start
    start = time.time()
    
def end_timer():
    duration = time.time() - start
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    milliseconds = (duration % 1) * 1000

    print(f"Finished analysis - duration: {hours:.0f}h {minutes:.0f}m {seconds:.0f}s {milliseconds:.0f}ms")

def load_ground_truth():
    ground_truth_path = Path(PROJECT_DIRECTORY / 'user study' / 'goal.tif')
    ground_truth = io.imread(ground_truth_path, plugin='pil')
    width = ground_truth.shape[1]
    offset = (width - 1311) // 2
    ground_truth = ground_truth[0:1311, offset:offset+1311]

    ground_truth = color.rgb2hsv(ground_truth)
    ground_truth = ground_truth[:, :, 0]

    if Path(PROJECT_DIRECTORY / 'user study' / 'goal_segments.npy').exists():
        ground_truth_segments = np.load(Path(PROJECT_DIRECTORY / 'user study' / 'goal_segments.npy'))
    else:
        ground_truth_segments = np.unique(ground_truth)
        print(f"Started Filtering Ground Truth Segments: {len(ground_truth_segments)}")
        ground_truth_segments = ground_truth_segments[0:MAX_SEGMENTS] if len(ground_truth_segments) > MAX_SEGMENTS else ground_truth_segments
        ground_truth_segments = [segment for segment in ground_truth_segments if (ground_truth == segment).sum() > MIN_SEGMENT_SIZE]
        print(f"Finished Filtering Ground Truth Segments: {len(ground_truth_segments)}")
        np.save(Path(PROJECT_DIRECTORY / 'user study' / 'goal_segments.npy'), ground_truth_segments)

    return ground_truth, ground_truth_segments

def load_result(user, file, shape):
    result = np.load(Path(PROJECT_DIRECTORY / 'user study' / user / (file + '.save')))
    width = result.shape[1]
    offset = (width - 2622) // 2
    result = result[0:2622, offset:offset+2622]
    result = cv2.resize(result, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)

    result_segments = np.unique(result)
    return result, result_segments


def jaccard_distance(segmentation, ground_truth):
    intersection = np.logical_and(segmentation, ground_truth)
    union = np.logical_or(segmentation, ground_truth)
    return 1 - intersection.sum() / union.sum()

def f1_score(segmentation, ground_truth):
    intersection = np.logical_and(segmentation, ground_truth)
    precision = intersection.sum() / segmentation.sum()
    recall = intersection.sum() / ground_truth.sum()
    return 2 * (precision * recall) / (precision + recall)

def total_error(segmentation, ground_truth):
    false_positives = np.logical_and(segmentation, np.logical_not(ground_truth))
    false_negatives = np.logical_and(np.logical_not(segmentation), ground_truth)
    return false_positives.sum() + false_negatives.sum()

def analyse(rank):
    if rank == 0:
        ground_truth, ground_truth_segments = load_ground_truth()
    else:
        ground_truth = None
        ground_truth_segments = None

    ground_truth = comm.bcast(ground_truth, root=0)
    ground_truth_segments = comm.bcast(ground_truth_segments, root=0)

    user = 'user ' + str((rank // 2) + 8)
    file = 'end' if rank % 2 == 1 else 'start'
    file = 'end'
    print(f"Loading result for {user} - {file}")
    result, result_segments = load_result(user, file, ground_truth.shape)
    accuracy = np.zeros(ground_truth.shape)

    best_total_segment = None
    best_total_distance = 1

    worst_total_segment = None
    worst_total_distance = 0

    total_distance = 0
    iterations = 0
    distances = []

    # plt.imshow(ground_truth)
    # plt.show()
    # plt.imshow(result)
    # plt.show()

    for ground_truth_segment in ground_truth_segments:
    # if True:
        # ground_truth_segment = 0.732
        best_fitting_segment = None
        best_distance = 1
        print(f"Analyzing segment {ground_truth_segment} for {user} - {file} - {len(ground_truth_segments)}")
        for result_segment in result_segments:
            distance = jaccard_distance(result == result_segment, ground_truth == ground_truth_segment)
            if distance < best_distance:
                best_distance = distance
                best_fitting_segment = result_segment
        print(f"Best fitting segment: {best_fitting_segment} - Distance: {best_distance}")
        if best_fitting_segment is not None:
            accuracy += result == best_fitting_segment
            total_distance += best_distance
            iterations += 1
            distances.append(best_distance)
            draw_single_segment(result, best_fitting_segment, ground_truth, ground_truth_segment, best_distance, fitting='best', user=user, file=file)
            
    print("Analysis complete")
    # plt.axis('off')
    # plt.title(f"Accuracy for {user} - {file}")
    # plt.imsave(str(Path(PROJECT_DIRECTORY / 'user study' / 'results' / f'{user}_{file}.png')), accuracy, cmap='gray')

    # with open(Path(PROJECT_DIRECTORY / 'user study' / 'results' / f'{user}_{file}.txt'), 'w') as file:
    #     file.write(f"mean: {np.mean(distances)}\n")
    #     file.write(f"median: {np.median(distances)}\n")
    #     file.write(f"std: {np.std(distances)}\n")
    #     file.write(f"min: {np.min(distances)}\n")
    #     file.write(f"max: {np.max(distances)}\n")


def draw_single_segment(result, segment, ground_truth, ground_truth_segment, distance, user, file, fitting = 'best'):
    fig, ax = plt.subplots(1, 1)
    intersection = np.logical_and(result == segment, ground_truth == ground_truth_segment)
    false_positives = np.logical_and(result == segment, np.logical_not(intersection))
    false_negatives = np.logical_and(ground_truth == ground_truth_segment, np.logical_not(intersection))

    bbox_segment = regionprops((result == segment).astype(int))[0].bbox
    bbox_ground_truth = regionprops((ground_truth == ground_truth_segment).astype(int))[0].bbox
    total_width = max(bbox_segment[3], bbox_ground_truth[3]) - min(bbox_segment[1], bbox_ground_truth[1])
    total_height = max(bbox_segment[2], bbox_ground_truth[2]) - min(bbox_segment[0], bbox_ground_truth[0])

    if total_width > total_height:
        total_height = total_width
    else:
        total_width = total_height

    center = ((bbox_segment[0] + bbox_segment[2]) // 2, (bbox_segment[1] + bbox_segment[3]) // 2)
    # Empty rgb image
    accuracy_map = np.zeros((result.shape[0], result.shape[1]))
    accuracy_map[false_positives] = [1, 0, .6]
    accuracy_map[intersection] = [1, 1, 1]
    accuracy_map[false_negatives] = [.8, 0, 1]

    ground_truth_path = Path(PROJECT_DIRECTORY / 'user study' / 'goal.tif')
    ground_truth = io.imread(ground_truth_path, plugin='pil')
    # image_path = Path(PROJECT_DIRECTORY / 'datasets' / 'example_medium_quality.tif')
    # image = io.imread(image_path, plugin='pil')
    # image = image[0:2622, round(1311/2):2622-round(1311/2)]
    # image = cv2.resize(image, (ground_truth.shape[1], ground_truth.shape[0]), interpolation=cv2.INTER_NEAREST)

    # ax.imshow(image[center[0] - total_height // 2:center[0] + total_height // 2, center[1] - total_width // 2:center[1] + total_width // 2], cmap='gray')
    # ax.imshow(accuracy_map[center[0] - total_height // 2:center[0] + total_height // 2, center[1] - total_width // 2:center[1] + total_width // 2], alpha=0.5)
    # ax.imshow(image, cmap='gray')
    ax.imshow(accuracy_map)
    ax.axis('off')
    ax.set_title(f"{fitting.title()} segment - Distance {distance} ")    

    plt.show()
    # fig.savefig(str(Path(PROJECT_DIRECTORY / 'user study' / 'results' / f'user_{user}_{file}_{fitting}_single_segment.png')))



if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        start_timer()

    analyse(rank)

    if rank == 0:
        end_timer()