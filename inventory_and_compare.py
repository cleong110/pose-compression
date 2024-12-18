from pathlib import Path
from pose_format import Pose
import itertools
import os
import json
import matplotlib.pyplot as plt

import plotly.express as px
import pandas as pd

def plot_sizes(data):

    # Extract data
    frames = []
    mp4_sizes = []
    pose_sizes = []
    pose_mp4_sizes = []

    for video_id, content in data.items():
        frames.append(content[".pose"]["frames"])
        mp4_sizes.append(content[".mp4"]["size_bytes"])
        pose_sizes.append(content[".pose"]["size_bytes"])
        pose_mp4_sizes.append(content[".pose.mp4"]["size_bytes"])

    # Convert sizes from bytes to megabytes for better readability
    mp4_sizes_mb = [size / 1_000_000 for size in mp4_sizes]
    pose_sizes_mb = [size / 1_000_000 for size in pose_sizes]
    pose_mp4_sizes_mb = [size / 1_000_000 for size in pose_mp4_sizes]

    # Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(frames, mp4_sizes_mb, label='.mp4', s=100, alpha=0.7)
    # plt.scatter(frames, pose_sizes_mb, label='.pose', s=100, alpha=0.7)
    plt.scatter(frames, pose_mp4_sizes_mb, label='.pose.mp4', s=100, alpha=0.7)

    # Labels and title
    plt.xlabel('Number of Frames')
    plt.ylabel('File Size (MB)')
    plt.title('File Size vs. Number of Frames')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Show plot
    plt.show()




def plot_file_size_vs_frames(data):
    """
    Plots an interactive scatter plot of file sizes vs. number of frames for .mp4, .pose, and .pose.mp4.

    Args:
        data (dict): Dictionary containing video data with file sizes and frame counts.
    """
    # Use only the first 3 entries for now
    # subset_data = {k: data[k] for k in list(data.keys())[:3]}

    # Prepare data for plotting
    rows = []
    for video_id, content in data.items():
        rows.append({"video_id": video_id, "type": ".mp4", "frames": content[".pose"]["frames"], "size_mb": content[".mp4"]["size_bytes"] / 1_000_000})
        rows.append({"video_id": video_id, "type": ".pose", "frames": content[".pose"]["frames"], "size_mb": content[".pose"]["size_bytes"] / 1_000_000})
        rows.append({"video_id": video_id, "type": ".pose.mp4", "frames": content[".pose"]["frames"], "size_mb": content[".pose.mp4"]["size_bytes"] / 1_000_000})
        rows.append({"video_id": video_id, "type": ".pose.zst", "frames": content[".pose"]["frames"], "size_mb": content[".pose.zst"]["size_bytes"] / 1_000_000})

    # Create a DataFrame
    df = pd.DataFrame(rows)

    # Plot using Plotly
    fig = px.scatter(
        df,
        x="frames",
        y="size_mb",
        color="type",
        hover_data=["video_id"],
        title=f"File Size vs. Number of Frames for {len(data.keys())} Youtube-ASL videos",
        labels={"frames": "Number of Frames", "size_mb": "File Size (MB)", "type": "File Type"}
    )

    fig.update_traces(marker=dict(size=10, opacity=0.7))

    # Show interactive plot
    fig.show()

def run_inventory(input_folder:Path, out_file="inventory.json")->dict:
    # print(input_folder)
    files = input_folder.rglob("*.mp4")
    mp4_files = [mp4_file for mp4_file in files if ".pose.mp4" not in mp4_file.name]

    names_sizes = {}
    extensions = [".mp4", ".pose", ".pose.mp4", ".pose.zst"]
    
    for file in itertools.islice(mp4_files, None):
        
        name_without_any_extensions = file.stem
        print(name_without_any_extensions)
        print(f"ID: {name_without_any_extensions}")
        names_sizes[name_without_any_extensions] = {}
        for suffix in extensions:
            file_dict = {}
            with_suffix = file.with_suffix(suffix)

            file_size = os.path.getsize(with_suffix)
            file_dict["size_bytes"] = file_size
            if with_suffix.is_file():
                print(with_suffix)

                if suffix == ".pose":
                    with with_suffix.open("rb") as f_in:
                        pose = Pose.read(f_in.read())

                        print(pose.body.data.shape)
                        print(pose.body)
                        frame_count = pose.body.data.shape[0]
                        file_dict["data_nbytes"] = pose.body.data.nbytes
                        file_dict["fps"] = pose.body.fps
                        file_dict["frames"] = frame_count
                        file_dict["persons"] = pose.body.data.shape[1]
                        file_dict["points"] = pose.body.data.shape[2]
                        file_dict["xyz"] = pose.body.data.shape[3]
                        

            names_sizes[name_without_any_extensions][suffix] = file_dict
    with open(out_file, "w") as f:
        json.dump(names_sizes, f)
    return names_sizes

if __name__ == "__main__":
    input_folder = Path("/home/vlab/data/testing_pose_compression/unique_to_laptop")

    data = {}
    with open("inventory.json", "r") as f:
        data = json.load(f)

    if not data:
        data = run_inventory(input_folder)




    # plot_sizes(names_sizes)
    

    plot_file_size_vs_frames(data)        
