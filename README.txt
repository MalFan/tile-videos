==================
Tile videos README
==================

:Authors:
    Desai Fan (2016-03)

:Version: 1.0

Introduction:
    This python program is used for combine multiple videos into a single tiled video, each of them with a time offset (delay).

Prerequisites:
    It requires OpenCV for python, numpy, ffmpeg and sox as prerequisites. 
    The python version is 2.7. The system is Mac OS X.

How to install these prerequisites?
    1. Install homebrew:
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    2. Install python:
        brew install python
    2. Install OpenCV and setting up in python. You might find this web page helpful:
        https://jjyap.wordpress.com/2014/05/24/installing-opencv-2-4-9-on-mac-osx-with-python-support/
    3. Install numpy:
        pip install numpy
    4. Install ffmpeg:
        brew install ffmpeg
    5. Install sox:
        brew install sox
    Note you might need to add "sudo" as a prefix to your command in case you encounter a "Permission denied" failure.

Usage:

Command line:
    python tile_videos.py [config.txt] [output_video.mp4]

Format of configuration file (note that at least two videos and at most nine videos are allowed.):
    [video_0.mp4] [start_time_in_seconds] [end_time_in_seconds] [offset_in_seconds]
    [video_1.mp4] [start_time_in_seconds] [end_time_in_seconds] [offset_in_seconds]
    [video_2.mp4] [start_time_in_seconds] [end_time_in_seconds] [offset_in_seconds]
    ...

Example:
    0.mp4 0 40 12.301
    1.mp4 0 38 23.320
    2.mp4 0 27 0.351
    3.mp4 0 14 6.852
    4.mp4 0 15 12.202
    5.mp4 0 13 2.203
    6.mp4 0 15 2.323
    7.mp4 0 13 3.302
    8.mp4 0 25 13.302
