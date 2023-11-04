import cv2
import numpy as np
import glob

# Termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points based on the checkerboard dimensions
objp = np.zeros((checkerboard_width * checkerboard_height, 3), np.float32)
objp[:,:2] = np.mgrid[0:checkerboard_height,0:checkerboard_width].T.reshape(-1, 2)

# Arrays to store object points and image points from all images
objpoints = [] # 3d points in real world space
imgpoints = [] # 2d points in image plane

# List of calibration images
images = glob.glob('calibration_images/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (checkerboard_height,checkerboard_width), None)

    # If found, add object points, image points
    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, (checkerboard_height,checkerboard_width), corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Camera calibration
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# mtx is the camera matrix
focal_length_x = mtx[0, 0]
focal_length_y = mtx[1, 1]
