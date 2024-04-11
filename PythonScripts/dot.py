import cv2
import numpy as np
import math

# 初始化窗口参数
height, width = 2000, 2000
center_x, center_y = width // 2, height // 2
radius = 500  # 圆形路径的半径

# 创建一个白色背景图像
image = np.zeros((height, width, 3), np.uint8) + 255

# 红点沿圆运动的角度
angle = 0

# 每次迭代改变的角度（以度为单位），控制速度
angle_change = 2

while True:
    # 计算红点的新位置
    x = int(center_x + radius * math.cos(math.radians(angle)))
    y = int(center_y + radius * math.sin(math.radians(angle)))

    # 创建一个全新的背景图像，如果想要看到完整轨迹可以移除这行代码
    image = np.zeros((height, width, 3), np.uint8) + 255

    # 在新位置上绘制红点
    cv2.circle(image, (x, y), 300, (0, 0, 255), -1)

    # 更新角度
    angle = (angle + angle_change) % 360

    # 显示图像
    cv2.imshow("Circular Motion", image)

    # 减慢速度，每次迭代暂停50毫秒
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

# 销毁所有OpenCV窗口
cv2.destroyAllWindows()
