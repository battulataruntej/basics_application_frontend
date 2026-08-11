# Experiment 01 — Image Scaling and Rotation Using Interpolation

## 1. Title

**Image Scaling and Rotation Using Nearest Neighbour and Bilinear Interpolation**

---

## 2. Objective

To develop a Python program that reads an image and performs:

1. Image scaling using **Nearest Neighbour Interpolation**
2. Image scaling using **Bilinear Interpolation**
3. Image rotation using **Nearest Neighbour Interpolation**
4. Image rotation using **Bilinear Interpolation**

The scaling, rotation, and interpolation operations are implemented manually without using OpenCV's built-in image transformation functions.

---

## 3. Software and Libraries Used

* Python 3
* NumPy
* OpenCV
* Google Colab

The following libraries are used:

```python
import cv2
import numpy as np
```

`OpenCV` is used for reading and displaying images, while `NumPy` is used for array manipulation and mathematical operations.

---

## 4. Constraints

The experiment follows the given constraints:

* OpenCV is used for image acquisition.
* Scaling is implemented from scratch.
* Rotation is implemented from scratch.
* Nearest neighbour interpolation is implemented from scratch.
* Bilinear interpolation is implemented from scratch.
* OpenCV functions such as `cv2.resize()` and `cv2.warpAffine()` are not used for scaling or rotation.

---

# 5. Image Acquisition

The input image is read using OpenCV:

```python
img = cv2.imread(filepath, 0)
```

The second argument `0` indicates that the image is loaded as a **grayscale image**.

The image is then converted into a NumPy array for further processing.

```python
in_img = np.array(img)
```

The input image used in this experiment is:

```text
cameraman_input.bmp.png
```

---

# 6. Image Scaling

Image scaling changes the dimensions of an image according to a specified scaling factor.

If the original image dimensions are:

[
W \times H
]

and the scaling factor is (s), then the new dimensions are:

[
W_{new}=sW
]

[
H_{new}=sH
]

In the program, the user enters the scaling factor:

```python
scaling_factor = int(input("Enter the scaling factor: "))
```

The program then creates an output array having the scaled dimensions.

---

# 7. Nearest Neighbour Scaling

## 7.1 Principle

Nearest neighbour interpolation assigns each pixel in the output image the value of the closest corresponding pixel in the input image.

For every destination pixel ((x_d,y_d)), the corresponding source coordinate is calculated as:

[
x_s=\frac{x_d}{s}
]

[
y_s=\frac{y_d}{s}
]

The coordinates are converted to integers to select the nearest source pixel.

In the implementation:

```python
x = int(i / scaling_factor)
y = int(j / scaling_factor)

scaled_image[i, j] = in_img[x, y]
```

Thus, the same source pixel may be copied to multiple output pixels when the image is enlarged.

---

## 7.2 Algorithm

For every pixel in the output image:

1. Determine its corresponding source coordinate.
2. Divide the destination coordinate by the scaling factor.
3. Convert the coordinate to an integer.
4. Copy the corresponding source pixel value.

### Pseudocode

```text
Read input image

Read scaling factor

Calculate new image dimensions

Create empty output image

For every pixel in output image:
    Calculate corresponding source x coordinate
    Calculate corresponding source y coordinate
    Select nearest source pixel
    Copy its intensity to output

Return scaled image
```

---

# 8. Bilinear Scaling

## 8.1 Principle

Bilinear interpolation uses the **four neighbouring pixels** around a fractional source coordinate.

Suppose the required point lies between four pixels:

```text
        Q11 -------- Q21
         |             |
         |      P      |
         |             |
        Q12 -------- Q22
```

The interpolated value is calculated using:

[
v(x,y)=
Q_{11}(1-d_x)(1-d_y)
+
Q_{21}d_x(1-d_y)
+
Q_{12}(1-d_x)d_y
+
Q_{22}d_xd_y
]

where:

[
d_x=x-x_1
]

[
d_y=y-y_1
]

The four neighbouring pixel values are obtained in the program using:

```python
Q11 = in_img[x1, y1]
Q21 = in_img[x2, y1]
Q12 = in_img[x1, y2]
Q22 = in_img[x2, y2]
```

The final interpolated value is:

```python
interpolated_value = (
    Q11 * (1 - dx) * (1 - dy)
    + Q21 * dx * (1 - dy)
    + Q12 * (1 - dx) * dy
    + Q22 * dx * dy
)
```

---

## 8.2 Source Coordinate Calculation

For each output pixel:

```python
src_x = i / scaling_factor
src_y = j / scaling_factor
```

These source coordinates can be fractional.

For example:

[
src_x=2.3
]

[
src_y=4.7
]

The four neighbouring pixels are then identified and used to calculate the interpolated intensity.

---

## 8.3 Bilinear Interpolation Function

The custom function:

```python
bilinear(in_img, src_x, src_y, w, h)
```

performs the interpolation.

The floor operation determines the top-left neighbouring pixel:

```python
x1 = int(np.floor(src_x))
y1 = int(np.floor(src_y))
```

The next neighbouring coordinates are obtained using:

```python
x2 = min(w - 1, x1 + 1)
y2 = min(h - 1, y1 + 1)
```

The `min()` operation prevents the coordinates from exceeding the image boundary.

---

# 9. Image Rotation

Image rotation changes the orientation of an image by an angle (\theta).

The standard rotation equations around the origin are:

[
x'=x\cos\theta-y\sin\theta
]

[
y'=x\sin\theta+y\cos\theta
]

However, directly mapping every input pixel to an output pixel can produce holes in the output image.

Therefore, this implementation uses **inverse mapping**.

---

# 10. Inverse Mapping

Instead of asking:

> Where does this input pixel go?

the algorithm asks:

> Which input pixel should be used for this output pixel?

For every output pixel:

```text
Output pixel
     ↓
Move relative to image centre
     ↓
Apply inverse rotation
     ↓
Obtain source coordinate
     ↓
Apply interpolation
     ↓
Assign pixel value
```

This prevents missing pixels in the rotated image.

---

# 11. Image Centre

The original image centre is calculated using:

```python
cx = w // 2
cy = h // 2
```

The new rotated image dimensions are calculated using:

[
W_{new}
=======

|W\cos\theta|
+
|H\sin\theta|
]

[
H_{new}
=======

|H\cos\theta|
+
|W\sin\theta|
]

The centre of the new image is then calculated:

```python
new_cx = new_w // 2
new_cy = new_h // 2
```

---

# 12. Rotation Using Nearest Neighbour

For every pixel in the output image, the algorithm first moves the coordinate relative to the new image centre:

```python
x = x_new - new_cx
y = y_new - new_cy
```

The corresponding source coordinate is then calculated using the inverse transformation.

The source coordinate is translated back to the original image coordinate system:

```python
x_old = x_old + cx
y_old = y_old + cy
```

Nearest neighbour interpolation is then applied:

```python
x_nn = int(round(x_old))
y_nn = int(round(y_old))
```

If the coordinates are within the input image boundary, the pixel is copied:

```python
if 0 <= x_nn < w and 0 <= y_nn < h:
    rotated[y_new, x_new] = img[y_nn, x_nn]
```

---

# 13. Rotation Using Bilinear Interpolation

The rotation process is similar to nearest neighbour rotation.

The difference occurs after obtaining the fractional source coordinate.

Instead of rounding the coordinate, the program retains the fractional values:

```python
x_old
y_old
```

The program then checks whether the source coordinate lies inside the input image:

```python
if 0 <= x_old < w and 0 <= y_old < h:
```

The custom bilinear interpolation function is then used:

```python
interpolated_value = bilinear(
    img,
    x_old,
    y_old,
    h,
    w
)
```

The four neighbouring pixels are used to calculate the final intensity.

Therefore, bilinear rotation produces smoother results than nearest neighbour rotation.

---

# 14. Comparison of Interpolation Methods

| Property              | Nearest Neighbour | Bilinear         |
| --------------------- | ----------------- | ---------------- |
| Number of pixels used | 1                 | 4                |
| Computation           | Simple            | More computation |
| Speed                 | Faster            | Slower           |
| Smoothness            | Lower             | Higher           |
| Image quality         | Lower             | Better           |
| Edges                 | Jagged/blocky     | Smoother         |
| Implementation        | Easy              | More complex     |

---

# 15. Scaling Example

Consider a scaling factor:

[
s=2
]

If the original image is:

[
256\times256
]

then:

[
W_{new}=256\times2=512
]

[
H_{new}=256\times2=512
]

Therefore, the output image becomes:

[
\boxed{512\times512}
]

For nearest neighbour interpolation, each output pixel obtains its value from the nearest corresponding input pixel.

For bilinear interpolation, the output pixel may be calculated from four neighbouring input pixels.

---

# 16. Rotation Example

Suppose the user enters:

[
\theta=45^\circ
]

The program converts the angle from degrees to radians:

```python
theta = np.deg2rad(theta)
```

This is necessary because NumPy's trigonometric functions use radians.

For example:

[
45^\circ=\frac{\pi}{4}
]

The new dimensions are then calculated using:

[
W_{new}
=======

|W\cos\theta|
+
|H\sin\theta|
]

[
H_{new}
=======

|H\cos\theta|
+
|W\sin\theta|
]

The rotated image is created with these dimensions.

---

# 17. Program Workflow

The complete workflow of the experiment is:

```text
                 Input Image
                      |
                      v
              OpenCV Image Read
                      |
                      v
              Grayscale Image
                      |
          +-----------+-----------+
          |                       |
          v                       v
       Scaling                 Rotation
          |                       |
     +----+----+             +----+----+
     |         |             |         |
     v         v             v         v
 Nearest    Bilinear      Nearest   Bilinear
 Neighbour  Interpolation Neighbour Interpolation
     |         |             |         |
     +----+----+             +----+----+
          |                       |
          v                       v
       Output                  Output
```

---

# 18. Files and Project Structure

The final submission should be organized as:

```text
Exp-01-<Roll-No>/
│
├── Code/
│   └── Experiment_1.ipynb
│
├── Input Images/
│   └── cameraman_input.bmp.png
│
├── Output Images/
│   ├── scaled_nearest.png
│   ├── scaled_bilinear.png
│   ├── rotated_nearest.png
│   └── rotated_bilinear.png
│
└── README.md
```

The complete folder should be compressed into:

```text
Exp-01-<Roll-No>.zip
```

---

# 19. Execution in Google Colab

The code can be executed directly in Google Colab.

### Step 1

Open the notebook:

```text
Experiment_1.ipynb
```

### Step 2

Upload the input image to the Colab environment.

### Step 3

Update the input image path if necessary:

```python
filepath = "/content/cameraman_input.bmp.png"
```

### Step 4

Run the scaling functions.

The program asks for:

```text
Enter the scaling factor:
```

Enter a value such as:

```text
2
```

### Step 5

Run the rotation functions.

The program asks for:

```text
Enter rotation angle in degrees:
```

For example:

```text
45
```

A positive angle represents counter-clockwise rotation, while a negative angle represents clockwise rotation according to the intended convention of the implementation.

---

# 20. Important Notes About the Implementation

The implementation uses array indexing in the form:

```python
image[row, column]
```

which corresponds to:

```text
image[y, x]
```

Therefore, when working with image coordinates, it is important to distinguish between:

* (x) → horizontal coordinate / column
* (y) → vertical coordinate / row

Care must also be taken when passing image dimensions to the interpolation function because NumPy image arrays are represented as:

```text
(height, width)
```

rather than:

```text
(width, height)
```

---

# 21. Result

The experiment demonstrates the implementation of image scaling and rotation using custom interpolation techniques.

The following transformations are implemented:

* Scaling using nearest neighbour interpolation
* Scaling using bilinear interpolation
* Rotation using nearest neighbour interpolation
* Rotation using bilinear interpolation

The experiment demonstrates that nearest neighbour interpolation is computationally simpler, while bilinear interpolation provides smoother image results by considering the four neighbouring pixels.

---

# 22. Conclusion

Image scaling and rotation were successfully implemented using Python and NumPy without relying on OpenCV's built-in geometric transformation functions.

Nearest neighbour interpolation selects the closest pixel and is therefore simple and computationally efficient. Bilinear interpolation considers four neighbouring pixels and calculates a weighted intensity value, resulting in smoother images.

The use of inverse mapping during rotation ensures that each destination pixel is mapped back to a corresponding source location, reducing holes and missing pixels in the transformed image.

Thus, the experiment provides a practical understanding of:

* Geometric image transformations
* Coordinate mapping
* Inverse mapping
* Nearest neighbour interpolation
* Bilinear interpolation
* Image scaling
* Image rotation
* Pixel-level image processing
