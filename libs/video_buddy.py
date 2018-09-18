import getopt
import os
import glob
import subprocess
import re
import eyed3


# Converts all files in a directory to desired media format
import sys


def fix_file_name(file_to_fix):
    new_file = re.sub('[-]...........[.]', '.', file_to_fix)
    os.rename(file_to_fix, new_file)
    return new_file


def fix_file_names(input_directory):
    input_pattern = input_directory + "/*"
    input_files = glob.glob(input_pattern)

    print("Sanitizing file names...")
    for media_file in input_files:
        fix_file_name(media_file)


def fix_quote(file_to_fix):
    new_file = file_to_fix.replace("'", "")
    os.rename(file_to_fix, new_file)


def fix_file_name_quotes(input_directory):
    input_pattern = input_directory + "/*"
    input_files = glob.glob(input_pattern)

    print("Sanitizing file names...")
    for media_file in input_files:
        fix_file_name(media_file)


def fix_tags(directory_path, artist, album):
    input_pattern = directory_path + "/*"
    input_files = glob.glob(input_pattern)

    print("Fixing tags...")
    for media_file in input_files:
        tag_audio_file(media_file, artist, album)


def tag_audio_file(file_to_tag, artist, album):
    mp3 = eyed3.load(file_to_tag)
    song_name = os.path.basename(file_to_tag).replace('.mp3', '')
    mp3.tag.title = song_name
    mp3.tag.artist = artist
    mp3.tag.album = album

    mp3.tag.save()


def get_shell_safe_file_name(input_name):
    # Format test name to prevent issues with protractor grep option
    name_chars = list(input_name)

    for index, char in enumerate(name_chars):
        if not char.isalnum() and not char.isspace() and char not in "\\":
            new_char = "'" + char
            name_chars[index] = new_char

    shell_safe_name = "".join(name_chars)

    return shell_safe_name


def get_videos(input_directory, input_extension, output_directory):
    # Get list of videos from input directory
    input_pattern = input_directory + "/*." + input_extension
    output_pattern = output_directory + "/*.mp3"
    input_files = [os.path.basename(x) for x in glob.glob(input_pattern)]
    output_files = [os.path.basename(x) for x in glob.glob(output_pattern)]

    # Get list of videos from output directory
    # Get a list of videos that have not yet been converted
    videos_not_converted = []
    extension_pattern = "\." + input_extension + "$"
    for video in input_files:
        converted_name_to_check = re.sub(extension_pattern, '.mp3', video)
        print("Checking if " + converted_name_to_check + " exists in " + output_directory)
        if converted_name_to_check in output_files:
            print("Video " + converted_name_to_check + " already exists in " + output_directory)
        else:
            print("Could not find " + re.sub(extension_pattern, '', video) + " in " + output_directory)
            full_video_path = input_directory + "/" + video
            videos_not_converted.append(full_video_path)
    return videos_not_converted


def convert_file(input_file_path, output_file_path, convert_command):
    # Call ffmpeg as blocking process
    final_command = convert_command.format(input_file_path, output_file_path)
    print("Running : " + final_command)
    did_succeed = False
    try:
        call_process = subprocess.Popen(final_command
                                        , stderr=subprocess.STDOUT
                                        , shell=True
                                        , preexec_fn=os.setsid
                                        )
        call_process.wait()
        did_succeed = True
    except:
        print("Error converting " + input_file_path)

    return did_succeed


def convert_videos(videos_to_convert, output_directory, error_log_name, convert_command, input_extension):
    total_videos = len(videos_to_convert)
    current_video = 1
    successful_conversions = 0
    failed_conversions = 0
    for video_path in videos_to_convert:

        print("Converting video " + str(current_video) + " of " + str(total_videos))

        extension_pattern = "\." + input_extension + "$"
        destination_name = re.sub(extension_pattern, '.mp4', os.path.basename(video_path))
        output_video_path = output_directory + "/" + destination_name
        outcome = convert_file(video_path, output_video_path, convert_command)

        if outcome is True:
            successful_conversions = successful_conversions + 1
            print("Successfully converted " + video_path + " !")

        elif outcome is not True:
            failed_conversions = failed_conversions + 1
            error_log_path = output_directory + error_log_name
            with open(error_log_path, "a+") as end_of_error_log:
                end_of_error_log.write(video_path)
            print("Could not convert " + video_path + " :(")

        else:
            raise RuntimeError("Check log, unhandled error occurred during conversion of " + video_path)

        current_video = current_video + 1

    print("Successfully converted " + str(successful_conversions) + " out of " + str(total_videos) + " files.")


def convert_ipad():
    # Parse any possible configuration options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                   ['inputPath=',
                                    'outputPath=',
                                    'inputExtension='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)

    input_path = ''
    output_path = ''
    input_extension = ''

    input_path_found = False
    output_path_found = False
    input_extension_found = False

    for o, a in opts:
        if o == "--inputPath":
            input_path = a
            print("Found option: " + o + " with value: " + a)
            input_path_found = True
        elif o == "--outputPath":
            output_path = a
            print("Found option: " + o + " with value: " + a)
            output_path_found = True
        elif o == "--inputExtension":
            input_extension = a
            print("Found option: " + o + " with value: " + a)
            input_extension_found = True
        else:
            assert False, "Unknown option found: " + o

    if input_path_found is not True:
        assert False, "Missing option --inputPath! Example --inputPath='myDir/dir' --outputPath='myDir/dir' " \
                      "--inputExtension='.mp4' "
    if output_path_found is not True:
        assert False, "Missing option --outputPath! Example --inputPath='myDir/dir' --outputPath='myDir/dir' " \
                      "--inputExtension='.mp4' "
    if input_extension_found is not True:
        assert False, "Missing option --inputExtension! Example --inputPath='myDir/dir' --outputPath='myDir/dir' " \
                      "--inputExtension='.mp4' "

    input_directory_path = input_path
    output_directory_path = output_path
    input_directory_extension = input_extension

    error_log = "conversion_errors.log"
    convert_command = './ffmpeg -y -i "{}" -movflags faststart -profile:v high -level 4.2 "{}" '

    fix_file_names(input_directory_path)
    videos_waiting_to_convert = get_videos(input_directory_path, input_directory_extension, output_directory_path)
    print("Number of videos found: " + str(len(videos_waiting_to_convert)))

    convert_videos(videos_waiting_to_convert
                   , output_directory_path
                   , error_log
                   , convert_command
                   , input_directory_extension)


def convert_mp3():
    # Parse any possible configuration options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                                   ['inputPath=',
                                    'outputPath=',
                                    'inputExtension='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        sys.exit(2)

    input_path = ''
    output_path = ''
    input_extension = ''

    input_path_found = False
    output_path_found = False
    input_extension_found = False

    for o, a in opts:
        if o == "--inputPath":
            input_path = a
            print("Found option: " + o + " with value: " + a)
            input_path_found = True
        elif o == "--outputPath":
            output_path = a
            print("Found option: " + o + " with value: " + a)
            output_path_found = True
        elif o == "--inputExtension":
            input_extension = a
            print("Found option: " + o + " with value: " + a)
            input_extension_found = True
        else:
            assert False, "Unknown option found: " + o

    if input_path_found is not True:
        assert False, "Missing option --inputPath! Example --inputPath='myDir/dir' --outputPath='myDir/dir' " \
                      "--inputExtension='.mp4' "
    if output_path_found is not True:
        assert False, "Missing option --outputPath! Example --inputPath='myDir/dir' --outputPath='myDir/dir' " \
                      "--inputExtension='.mp4' "
    if input_extension_found is not True:
        assert False, "Missing option --inputExtension! Example --inputPath='myDir/dir' --outputPath='myDir/dir' " \
                      "--inputExtension='.mp4' "

    input_directory_path = input_path
    output_directory_path = output_path
    input_directory_extension = input_extension

    artist = "STREETS"
    album = "RAGE"

    error_log = "conversion_errors.log"
    convert_command = './ffmpeg -y -i "{}" -vn -sn -c:a mp3 -ab 192k "{}" '

    fix_file_names(input_directory_path)
    videos_waiting_to_convert = get_videos(input_directory_path, input_directory_extension, output_directory_path)
    print("Number of files found: " + str(len(videos_waiting_to_convert)))

    convert_videos(videos_waiting_to_convert
                   , output_directory_path
                   , error_log
                   , convert_command
                   , input_directory_extension)

    fix_tags(output_directory_path, artist, album)

