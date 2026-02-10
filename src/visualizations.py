import os
import cv2
import glob
import re
import pathlib
import numpy as np
import matplotlib.pyplot as plt

def make_video(
        img_folder_name, # folder where imgs are stored
        fps = 1 # files per second
        ):

    l = glob.glob(f"{img_folder_name}/*.png") # list of filenames

    # assuming the files are called "000.png", "001.png", etc.;
    # to plot them in the right order:
    # remove ".png" from filenames;
    # then, convert filenames to integer
    m = [int(re.findall(r'\d+.png', item)[0].replace(".png", "")) for item in l]
    # and finally, sort:
    images = [l[i] for i in np.argsort(m)]

    # make a "video" subfolder in images folder
    os.makedirs(pathlib.Path(img_folder_name, "video"), exist_ok=True)

    # define file name for video
    video_name = str(pathlib.Path(img_folder_name, "video", "video.mp4"))

    # if there was already such a file - remove it
    if os.path.exists(video_name):
        os.remove(video_name)
        print("\t previous video removed")

    # generate frame in cv2
    frame = cv2.imread(images[0])
    height, width, _ = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(
        video_name,
        fourcc,
        fps, # frames per second = this is the speed of our video
        (width,height)
    )

    # add images as separate frames
    for image in images:
        video.write(
            cv2.resize(
                cv2.imread(image),
                (width, height)
                ),
        )
    cv2.destroyAllWindows()

    # save
    video.release()

    return None

def create_plots(routed_edges_gdf, seed_points_snapped, streetcolor, edgecolor, seedcolor, lws):
    for rank in sorted(routed_edges_gdf["rank"].unique()):
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # first, plot street network as "base line"
        routed_edges_gdf.plot(
            ax=ax,
            color=streetcolor,
            lw=lws["street"],
            zorder=0
        )

        # plot all edges up to current rank

        routed_edges_gdf[routed_edges_gdf["rank"] <= rank].plot(
            ax=ax,
            color=edgecolor,
            lw=lws["bike"],
            zorder=1
        )

        seed_points_snapped.plot(
            ax=ax,
            color=seedcolor,
            zorder=2
        )

        ax.set_axis_off()

        plot_id = "{:03d}".format(rank)  # format plot ID with leading zeros

        fig.savefig(f"./results/plots/{plot_id}.png", dpi=300)

        plt.close()

        return None