import cv2
import numpy as np
import math
import struct


def predict(img):
    x, y = img.shape
    img = img.astype(int)
    predicted = np.zeros(int(x*y), dtype=int)
    predicted[0] = img[0, 0]

    for i in range(1, x):
        predicted[i] = img[i - 1, 0] - img[i, 0]
    for j in range(1, y):
        predicted[int(i*x)] = img[0, j - 1] - img[0, j]
    for i in range(1, x):
        for j in range(1, y):
            if img[i - 1, j - 1] >= max(img[i - 1, j], img[i, j - 1]):
                value = min(img[i - 1, j], img[i, j - 1])
            elif img[i - 1, j - 1] <= min(img[i - 1, j], img[i, j - 1]):
                value = max(img[i - 1, j], img[i, j - 1])
            else:
                value = img[i - 1, j] + img[i, j - 1] - img[i - 1, j - 1]
            predicted[int(j*x+i)] = value - img[i, j]
    return predicted, x,y


def encode(predicted,x,y):
    flattened = predicted
    nc = np.zeros_like(flattened)
    nc[0] = flattened[0]
    for i in range(1, len(flattened)):
        if flattened[i] >= 0:
            nc[i] = flattened[i] * 2
        else:
            nc[i] = abs(flattened[i]) * 2 - 1
        nc[i] += nc[i - 1]

    header = struct.pack("IIBI", x, len(nc), nc[0],nc[len(nc)-1])
    compressed_data = bytearray(header)

    def recursive_encode(L, H):
        if H - L <= 1 or nc[L] == nc[H]:
            return
        m = (H + L) // 2
        g = math.ceil(math.log2(nc[H] - nc[L] + 1))
        value = nc[m] - nc[L]

        compressed_data.extend(int(value).to_bytes((g + 7) // 8, "big"))
        if L<m:
            recursive_encode(L, m)
        if m < H:
            recursive_encode(m, H)

    recursive_encode(0, len(nc) - 1)
    return compressed_data


def compress_image(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found at {input_path}")

    predicted ,x,y= predict(img)
    compressed_data = encode(predicted,x,y)

    with open(output_path, "wb") as f:
        f.write(compressed_data)


def decode(compressed_data):
    header_size = struct.calcsize("IIBI")
    x, length, first_value,last_value = struct.unpack("IIBI", compressed_data[:header_size])
    y = length/x
    nc = np.zeros(length)
    nc[0] = first_value
    nc[length-1] = last_value


    def recursive_decode(L, H):
        if H - L <= 1:
            return
        if nc[L]==nc[H]:
            for i in range(L+1,H):
                nc[i] = nc[L]
        m = (H + L) // 2

        g = math.ceil(math.log2(nc[H] - nc[L] + 1))
        value_size = (g + 7) // 8
        value_bytes = compressed_data[recursive_decode.index:recursive_decode.index + value_size]
        recursive_decode.index += value_size
        value = int.from_bytes(value_bytes, "big")

        nc[m] = nc[L] + value
        if L < m:
            recursive_decode(L, m)
        if m <H:
            recursive_decode(m, H)

    recursive_decode.index = header_size
    recursive_decode(0, int(length - 1))
    return nc,x,y,length


def decompress(nc,x,y):
    x = int(x)
    y = int(y)
    img = np.zeros((x, y), dtype=int)
    img[0, 0] = nc[0]

    for i in range(1, x):
        img[i, 0] = img[i - 1, 0] - nc[i]
    for j in range(1, y):
        img[0, j] = img[0, j - 1] - nc[int(j* x)]
    for i in range(1, x):
        for j in range(1, y):
            if img[i - 1, j - 1] >= max(img[i - 1, j], img[i, j - 1]):
                value = min(img[i - 1, j], img[i, j - 1])
            elif img[i - 1, j - 1] <= min(img[i - 1, j], img[i, j - 1]):
                value = max(img[i - 1, j], img[i, j - 1])
            else:
                value = img[i - 1, j] + img[i, j - 1] - img[i - 1, j - 1]
            img[i, j] = value - nc[int(j*x+i)]
    return img

def decompress_image(input_path, output_path):
    with open(input_path, "rb") as f:
        compressed_data = f.read()

    C,x,y,length = decode(compressed_data)


    N = np.zeros(length, dtype=int)
    N[1:] = C[1:] - C[:-1]

    E = np.zeros(length, dtype=int)
    E[0] = C[0]
    E[1:] = np.where(N[1:] % 2 == 0, N[1:] // 2, -(N[1:] + 1) // 2)
    img = decompress(E,x,y)


    cv2.imwrite(output_path, img)
def decompress_image_show(input_path):
    with open(input_path, "rb") as f:
        compressed_data = f.read()

    C, x, y, length = decode(compressed_data)

    N = np.zeros(length, dtype=int)
    N[1:] = C[1:] - C[:-1]

    E = np.zeros(length, dtype=int)
    E[0] = C[0]
    E[1:] = np.where(N[1:] % 2 == 0, N[1:] // 2, -(N[1:] + 1) // 2)
    img = decompress(E, x, y)
    img = np.clip(img, 0, 255).astype(np.uint8)
    cv2.imshow("Decompressed Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

input_image = "result.jpg"
compressed_file = "compressed_image.bin"
decompressed_image = "decompressed_image.jpg"
compress_image(input_image, compressed_file)
decompress_image(compressed_file, decompressed_image)
