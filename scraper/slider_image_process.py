import base64
import random
import cv2 as cv
import numpy as np

from PIL import Image

def is_monochrome(imagePath: str):
    """从路径检验纯色图片"""
    image = Image.open(imagePath)
    pixels = list(image.getdata())
    return all(pixel == pixels[0] for pixel in pixels)


def base64_to_img(data):
    """base64数据转opencv图片对象"""
    image_data = base64.b64decode(str(data).split(',')[-1], altchars=None, validate=False)
    np_array = np.frombuffer(image_data, np.uint8)
    image = cv.imdecode(np_array, cv.IMREAD_UNCHANGED)

    return image


def cutting_transparent_block(imageSrc: cv.typing.MatLike, offset: int = 0):
    """
    切除图片的透明部分(判断方向左向右)
    offset : 预设定图片右边界，避免无意义检测
    """
    if imageSrc.shape[2] != 4:
        raise RuntimeError("Image must have alpha channel")

    if offset == 0:
        offset = imageSrc.shape[1]

    image = imageSrc[0:imageSrc.shape[0], 0:offset]
    point_0 = [offset, image.shape[0]]
    point_1 = [0, 0]

    # 查找有效图像的边界
    for pixel_y in range(0, image.shape[0]):
        for pixel_x in range(0, image.shape[1]):
            if image[pixel_y, pixel_x][3] != 0:
                if point_0[0] > pixel_x:
                    point_0[0] = pixel_x
                if point_0[1] > pixel_y:
                    point_0[1] = pixel_y

                if point_1[0] < pixel_x:
                    point_1[0] = pixel_x
                if point_1[1] < pixel_y:
                    point_1[1] = pixel_y

    point_1[0] += 1
    point_1[1] += 1

    return image[point_0[1]:point_1[1], point_0[0]:point_1[0]]


def get_tracks(distance):
    """
    生成非匀速的滑块位移路径
    参考 https://blog.csdn.net/La_vie_est_belle/article/details/130161844
    """
    tracks = []  # 移动轨迹
    current = 0  # 位移
    mid = distance * 3 / 5  # 减速阈值
    t = 0.2  # 计算间隔
    v = 0  # 初始速度

    while current < distance:
        # 加速度
        if current < mid:
            a = random.randint(3, 5)
        else:
            a = random.randint(-5, -3)

        v0 = v  # 初速度 v0
        v = v0 + a * t  # 当前速度
        move = v0 * t + 1 / 2 * a * t * t  # 移动距离
        current += move
        tracks.append(round(current))

    tracks[-1] = distance
    # print(tracks)
    return tracks

def image_binary_sum(image: cv.typing.MatLike, offset: int = 0):
    """返回图片二值化后每列像素和"""
    image_gray = cv.cvtColor(image, cv.COLOR_BGRA2GRAY)
    _, image_bin = cv.threshold(image_gray, 0, 255, cv.THRESH_BINARY)

    if offset == 0:
        offset = image_bin.shape[1]

    list_pixel_total = []
    for pixel_x in range(0, offset):
        pixel_total = 0
        for pixel_y in range(0, image_bin.shape[0]):
            if image_bin[pixel_y][pixel_x]:
                pixel_total += 1
        list_pixel_total.append(pixel_total)

    # plt测试代码
    # y = list_pixel_total
    # x = list(range(slide_bg_img_bit.shape[1]))
    # plt.figure(figsize=(8, 5))
    # plt.plot(x, y, c="g", marker='D', markersize=5)
    # plt.savefig('file.png')

    return list_pixel_total


def check_special_block(image: cv.typing.MatLike):
    """检测特定方块:左侧突起"""
    special_block_list = [1, 9, 11, 13, 15, 17]
    # print(image_binary_sum(image))
    block_list = image_binary_sum(image, offset=len(special_block_list))[0:len(special_block_list)]
    return block_list == special_block_list


def identify_gap(slide_bg_img: cv.typing.MatLike, slide_block_img: cv.typing.MatLike):
    """识别拼图缺口(左上角)坐标"""
    slide_block_img_gray = cv.cvtColor(slide_block_img, cv.COLOR_BGRA2GRAY)
    slide_bg_img_gray = cv.cvtColor(slide_bg_img, cv.COLOR_BGRA2GRAY)

    _, slide_block_img_bin = cv.threshold(slide_block_img_gray, 254, 255, cv.THRESH_BINARY)
    _, slide_bg_img_bin = cv.threshold(slide_bg_img_gray, 50, 255, cv.THRESH_BINARY)

    result = cv.matchTemplate(slide_block_img_bin, slide_bg_img_bin, cv.TM_CCOEFF)
    _, maxVal, _, maxLoc = cv.minMaxLoc(result)

    # cv.circle(slide_bg_img_bin, maxLoc, 3, (0, 0, 0), 3)
    # cv.imshow("slide_bg_img", slide_bg_img_bin)
    # print('maxVal=', maxVal)

    return maxLoc