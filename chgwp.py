#!/usr/bin/python
"""Uses Cocoa classes via PyObjC to set a random desktop picture on all screens.
Tested on Mountain Lion and Mavericks (and Yosemite - BCW).

See:
https://developer.apple.com/library/mac/documentation/cocoa/reference/applicationkit/classes/NSWorkspace_Class/Reference/Reference.html
https://developer.apple.com/library/mac/documentation/Cocoa/Reference/Foundation/Classes/NSURL_Class/Reference/Reference.html
https://developer.apple.com/library/mac/documentation/cocoa/reference/applicationkit/classes/NSScreen_Class/Reference/Reference.html
"""

import sys
import os
import argparse
import glob
import random
import subprocess

from AppKit import NSWorkspace, NSScreen
from Foundation import NSURL


def change_desktop_background(file, desk_id):
    """Function that applies the named file as wallaper for the specified
    monitor (desk_id)"""
    file_url = NSURL.fileURLWithPath_(file)
    screen   = NSScreen.screens()[desk_id]
    ws       = NSWorkspace.sharedWorkspace()
    ws.setDesktopImageURL_forScreen_options_error_(file_url, screen, {}, None)

# Determine number of monitors currently active.
num_mon = len(NSScreen.screens())
mon_rng = range(0,num_mon)

# Path to wallpaper files, with trailing path separator. Note that the path
# could be different, and be specified individually for each entry in the
# wallpaper dictionary below.
wp_dir = os.environ.get('WALLPAPER')
if wp_dir is None:
    print 'Error: Environment variable specifying path to wallpaper folder '\
          'not defined: $WALLPAPER'
    sys.exit()
if not os.path.exists(wp_dir):
    print 'Error: Specified path for wallpaper folder does not exist: ',wp_dir
    sys.exit()

parser = argparse.ArgumentParser(description="Set wallpaper on all or "
             "specified desktop to specified theme or random selection.")
parser.add_argument("-t","--theme",
    help="Desired theme (Determined by tags set for images in wallpaper folder")
parser.add_argument("-d","--desktop",
    help="Desired desktop (Numbered from left to right, starting from 0.")
args = parser.parse_args()

if args.theme:  # A particular "theme" was specified
    v = args.theme
    v = v.lower()  # Force upper case for matching below
    print 'Option specified: '+v
    p = subprocess.Popen(['mdfind','-onlyin',wp_dir,'kMDItemUserTags == wp_'+v],
                         stdout=subprocess.PIPE)
    (output,err) = p.communicate()
    if err is not None:
        print "Houston, we have a problem."
        sys.exit()
    pictures_list = output.split('\n')
    if len(pictures_list) == 1:
        print "No images found with tag: ",v
        sys.exit()
    else:
        pictures_list = pictures_list[0:-1]  # remove trailing blank entry
else:  # No theme specified, use desired default setting
    print 'No options specified, choosing randomly from specified folder.'
    pictures_list = glob.glob(wp_dir+'*.*')

if len(pictures_list) == 0:
    print "No images found at specified location: ",wp_dir
    sys.exit()

if args.desktop:
    mon_rng = [int(args.desktop)]

for dndx in mon_rng:
    # Choose randonly from images tagged with the specified theme.
    wp_path = random.choice(pictures_list)
    # Remove selected entry from list so we don't get duplicate images.
    pictures_list[:] = [wp for wp in pictures_list if wp_path not in wp]
    print "To monitor",dndx,"applying",wp_path
    change_desktop_background(wp_path,dndx)

# mdls -name "kMDItemUserTags" ~/Drop_box/Wallpapers/*.*|grep -v "("|grep -v ")"
# p = subprocess.call(['mdls','-onlyin',wp_dir,'kMDItemUserTags == '+v])
# print pictures_list
# print len(pictures_list)
# import xattr
# from struct import unpack
#
# wp_tag = 'com.apple.metadata:_kMDItemUserTags'
# dndx = 0
# for pic in p:
#     attrs = xattr.xattr(pic) #, "com.apple.metadata:_kMDItemUserTags", {})
#     if wp_tag in attrs:
#         tags = attrs.get(wp_tag)
#        #ltag = len(tags)
#        #uptags = unpack(ltag*'B', tags)
#        #print uptags
#         if v in tags:
#             print tags
#             if dndx < mon_rng:
#                 change_desktop_background(pic,dndx)
#                 dndx += 1
#             if dndx == num_mon:
#                 sys.exit()
