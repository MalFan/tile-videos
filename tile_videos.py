import cv2
import numpy as np
import sys
import subprocess

def create_blank(width=640, height=360, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


def combine_images(images, num_videos):
    num_images = len(images)

    assert(num_videos >= 2 and num_videos <= 9)
    blank_img = create_blank()

    # Layout arrangement
    if num_images == 1:
        vis = images[0]
    elif num_images == 2:
        vis = np.concatenate((images[0], images[1]), axis=1)
    elif num_images == 3:
        vis1 = np.concatenate((images[0], images[1]), axis=1)
        vis2 = np.concatenate((images[2], blank_img), axis=1)
        vis = np.concatenate((vis1, vis2), axis=0)
    elif num_images == 4:
        vis1 = np.concatenate((images[0], images[1]), axis=1)
        vis2 = np.concatenate((images[2], images[3]), axis=1)
        vis = np.concatenate((vis1, vis2), axis=0)
    elif num_images == 5:
        vis1 = np.concatenate((images[0], images[1], images[2]), axis=1)
        vis2 = np.concatenate((images[3], images[4], blank_img), axis=1)
        vis = np.concatenate((vis1, vis2), axis=0)
    elif num_images == 6:
        vis1 = np.concatenate((images[0], images[1], images[2]), axis=1)
        vis2 = np.concatenate((images[3], images[4], images[5]), axis=1)
        vis = np.concatenate((vis1, vis2), axis=0)
    elif num_images == 7:
        vis1 = np.concatenate((images[0], images[1], images[2]), axis=1)
        vis2 = np.concatenate((images[3], images[4], images[5]), axis=1)
        vis3 = np.concatenate((images[6], blank_img, blank_img), axis=1)
        vis = np.concatenate((vis1, vis2, vis3), axis=0)
    elif num_images == 8:
        vis1 = np.concatenate((images[0], images[1], images[2]), axis=1)
        vis2 = np.concatenate((images[3], images[4], images[5]), axis=1)
        vis3 = np.concatenate((images[6], images[7], blank_img), axis=1)
        vis = np.concatenate((vis1, vis2, vis3), axis=0)
    else:
        vis1 = np.concatenate((images[0], images[1], images[2]), axis=1)
        vis2 = np.concatenate((images[3], images[4], images[5]), axis=1)
        vis3 = np.concatenate((images[6], images[7], images[8]), axis=1)
        vis = np.concatenate((vis1, vis2, vis3), axis=0)

    return vis

def tile_video(config_file, output_file):
    video_names = []
    starting_times = []
    starting_frames = []
    durations = []
    stopping_frames = []
    offsets = []
    skipping_frames = []

    # width/height pattern
    wh_pattern = {'1':(640, 360),
                  '2':(1280, 360),
                  '3':(1280, 720), '4':(1280, 720),
                  '5':(1920, 720), '6':(1920, 720),
                  '7':(1920, 1080), '8':(1920, 1080), '9':(1920, 1080)}

    with open(config_file, 'r') as f:
        for line in f:
            video_content = line.rstrip('\n').split(' ')

            # What do we have in the config file?
            # Each line has:
            # 1. file name / url
            # 2. starting time of that video
            # 3. ending time of that video
            # 4. global offset
            video_names.append(video_content[0])

            starting_time = float(video_content[1])
            starting_times.append(starting_time)

            duration = float(video_content[2]) - starting_time
            durations.append(duration)

            offset = float(video_content[3])
            offsets.append(offset)

            # Calculate global starting and stopping frame
            fps = 25 # Usually 25
            # How many frames should this video skip. Defined by starting time.
            skipping_frames.append(int(round(fps * starting_time)))
            # At which global frame should this video play. Defined by offset.
            starting_frames.append(int(round(fps * offset)))
            # At which global frame should this video stop. Defined by offset and duration.
            stopping_frames.append(int(round(fps * (duration + offset))))


    num_videos = len(video_names)

    if num_videos > 9:
        print('Sorry, we could at most handle 9 videos.')
        exit()
    elif num_videos < 2:
        print('You should have at least 2 videos to combine them.')
        exit()

    caps = []
    for i in range(num_videos):
        # Create caps
        cap = cv2.VideoCapture(video_names[i])
        # Skip some frames
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, skipping_frames[i])
        caps.append(cap)

        # Set the cap video width & height might speed things up!!

        # print(cap.get(cv2.cv.CV_CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')

    out = cv2.VideoWriter(output_file, fourcc, 25, wh_pattern[str(num_videos)])

    # Size of each tile is:
    width = 640
    height = 360

    played = [0] * num_videos
    blank_img = create_blank()
    global_frame = 0
    print('--------------------')
    print('Processing frames...')
    print('--------------------')
    while True:

        # Print to stdout
        if global_frame % 25 == 0:
            print('Frame: %d' % (global_frame))

        playing = 0
        images = []
        for i in range(num_videos):
            if global_frame >= starting_frames[i] and global_frame <= stopping_frames[i]:
                ret, frame = caps[i].read()
                if ret == True:
                    played[i] = 1
                    playing += 1
                    images.append(cv2.resize(frame, (width, height), interpolation=cv2.INTER_CUBIC))

                    # # cv2.imshow('frame',frame)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                else:
                    images.append(blank_img)
            else:
                images.append(blank_img)

        if playing == 0 and sum(played) == num_videos:
            break

        vis = combine_images(images, num_videos)

        out.write(vis)

        global_frame += 1

    # Close everything
    for i in range(num_videos):
        caps[i].release()
    out.release()
    cv2.destroyAllWindows()



def mix_audio(config_file, audio_file):
    print('----------------')
    print('Mixing audios...')
    print('----------------')
    with open(config_file, 'r') as f:
        delayed_audios = []
        for line in f:
            arr = line.rstrip().split(' ')
            mp4_file = arr[0]
            start = arr[1]
            end = arr[2]
            offset = arr[3]

            file_name = arr[0].split('.')[0]
            mp3_file = file_name + '.mp3'
            trimmed_mp3_file = file_name + '_trimmed.mp3'
            delayed_mp3_file = file_name + '_delayed.mp3'

            # Extract audio
            subprocess.call('ffmpeg -i %s -b:a 192K -vn %s' % (mp4_file, mp3_file), shell=True)
            # Trim audio according to start and end
            subprocess.call('sox %s %s trim %s =%s' % (mp3_file, trimmed_mp3_file, start, end), shell=True)
            # Add offset to audio
            subprocess.call('sox %s %s pad %s' % (trimmed_mp3_file, delayed_mp3_file, offset), shell=True)
            # Remove temp audio
            subprocess.call('rm %s' % (trimmed_mp3_file), shell=True)
            subprocess.call('rm %s' % (mp3_file), shell=True)
            delayed_audios.append(delayed_mp3_file)

        subprocess.call('sox -m %s %s' % (' '.join(delayed_audios), audio_file), shell=True)

        for delayed_audio in delayed_audios:
            # Remove temp temp delayed audio
            subprocess.call('rm %s' % (delayed_audio), shell=True)



def combine(video_file, audio_file, output_file):
    print('----------------------------')
    print('Combining video and audio...')
    print('----------------------------')
    subprocess.call("ffmpeg -i %s -i %s -shortest %s" % (video_file, audio_file, output_file), shell=True)


def remove_temp_files(video_file, audio_file):
    subprocess.call('rm %s' % (video_file), shell=True)
    subprocess.call('rm %s' % (audio_file), shell=True)


if __name__ == '__main__':
    config_file = sys.argv[1]
    output_file = sys.argv[2]

    tile_video(config_file, 'video_temp.mp4')
    mix_audio(config_file, 'audio_temp.mp3')

    combine('video_temp.mp4', 'audio_temp.mp3', output_file)

    remove_temp_files('video_temp.mp4', 'audio_temp.mp3')
