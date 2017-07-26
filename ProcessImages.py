#!/usr/local/bin/python2.7

import os
from PIL import Image


class ProcessImages:
    def __init__(self):
        self.img_folder = 'screens/'
        self.mask_color = (221, 221, 221, 255)

        self.top_left = (649, 146)
        self.top_right = (1304, 146)
        self.bottom_left = (648, 938)
        self.bottom_right = (1304, 938)

    def crop_tuple(self):
        tup = (self.top_left[0], self.top_left[1], self.top_right[0], self.bottom_left[1])
        print tup
        return tup

    # img2 = im.crop((left, upper, right, lower))

    def get_pngs(self):
        mypath = self.img_folder
        onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        sorted_images = sorted([f for f in onlyfiles if f.endswith('.png')])
        sorted_images = [os.path.join(self.img_folder, f) for f in sorted_images]
        return sorted_images

    def percent_img(self, percent, length):
        return int(percent * length)

    def find_edge(self, pixels):

        found_mask = False
        for index, pixel in enumerate(pixels):
            if found_mask:
                if pixel != self.mask_color:
                    return index
            else:
                if pixel == self.mask_color:
                    found_mask = True
        print 'Did not find mask color'


    def crop_png(self, filename):

        page, shot = filename.split('.png')[0].split('_')
        img_path = os.path.join(self.img_folder, filename)
        im = Image.open(img_path)
        width, height = im.size
        pix = im.load()

        horizontal = [self.percent_img(x, width) for x in [0.25, 0.50, 0.75]]
        vertical = self.percent_img(0.50, height)

        #print horizontal, vertical

        horizontal_strip = [pix[x, vertical] for x in range(width)]
        vertical_strip_left = [pix[horizontal[0], y] for y in range(height)]
        vertical_strip_center = [pix[horizontal[1], y] for y in range(height)]
        vertical_strip_right = [pix[horizontal[2], y] for y in range(height)]

        if shot == '1':

            left = self.find_edge(horizontal_strip)
            upper = self.find_edge(vertical_strip_center)
            right = self.find_edge(list(reversed(horizontal_strip)))
            lower = self.find_edge(vertical_strip_left)

            print left, upper, right, lower
            right = width - right - left
            lower -= upper

        else:
            return

        print left, upper, right, lower

        img2 = im.crop((left, upper, right, lower))
        img2.save('screens/test2.png')

        # print pix[141, 181]
        # print pix[141, 181] == self.mask_color

        # img2 = im.crop((0, 0, 100, 100))
        # img2 = im.crop((100, 0, 200, 100))
        # img2.save('screens/test2.png')

    def crop_pngs(self):
        """
        images = self.get_pngs()
        for f in images:
            self.crop_png(f)
        """

        for f in self.get_pngs():
            im = Image.open(f)
            img2 = im.crop(self.crop_tuple())
            img2.save(f)



try:
    k = ProcessImages()
    k.crop_pngs()
except Exception, e:
    print str(e)

