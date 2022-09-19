import os
import pytesseract
from PIL import Image
from collections import defaultdict

# --- pytesseract path ---
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"


# --- 獲取圖片中 像素點數量最多的像素 ---
def get_threshold(image):
    pixel_dict = defaultdict(int)
    # 像素及該像素出現次數最多的字典
    rows, cols = image.size
    for i in range(rows):
        for j in range(cols):
            pixel = image.getpixel((i, j))
            pixel_dict[pixel] += 1
    # --- 獲取像素出現最多的次數 ---
    count_max = max(pixel_dict.values())
    pixel_dict_reverse = {v: k for k, v in pixel_dict.items()}
    # --- 戶戳線次數最多的像素點 ---
    threshold = pixel_dict_reverse[count_max]
    return threshold


# 按照閥值進行二值化處理
# threshold: 像素閥值
def get_bin_table(threshold):
    #  --- 獲取灰階轉二值的映射table ---
    table = []
    for i in range(256):
        rate = 0.1  # 在threshold的適當範圍內進行處理
        if threshold*(1-rate)<= i <= threshold*(1+rate):
            table.append(1)
        else:
            table.append(0)
    return table


# --- 去掉二值化處理後的圖片中的噪音點 ---
def cut_noise(image):
    rows, cols = image.size     # 圖片的寬, 高
    change_pos = []             # 紀錄噪音點位置
    # --- 遍歷圖片中的每個點, 除掉邊緣 ---
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            # pixel_set 用來記錄該店附近的黑色像素的數量
            pixel_set = []
            # 取得該點的領域為以該點為中心的九宮格
            for m in range(i-1, i+2):
                for n in range(i-1, i+2):
                    if image.getpixel((m, n)) != 1:  # 1為白色, 0為黑色
                        pixel_set.append(image.getpixel((m, n)))

            # --- 若該位置的九宮格內的黑色數量>=4, 判斷為噪音 ---
            if len(pixel_set) <= 4:
                change_pos.append((i, j))

        # --- 對相應位置進行像素修改, 將要噪音處的像素設為1(白色) ---
        for pos in change_pos:
            image.putpixel(pos, 1)

        return image    # 返回修改後的照片


def OCR_lmj(img_path):
    # --- 打開圖片文件 ---
    image = Image.open(img_path)
    # --- 轉化為灰階 ---
    imgry = image.convert('L')
    out = imgry

    # --- 獲取圖片中的出現次數最多的像素, 即為該圖片的背景 ---
    # max_pixel = get_threshold(imgry)
    # --- 將圖片進行二值化處理 ---
    # table = get_bin_table(threshold=max_pixel)
    # out = imgry.point(table, '1')
    # --- 去掉圖片中的噪音 (孤立點) ---
    out = cut_noise(out)
    # --- 保存圖片 ---
    # out.save()
    # --- 僅 識別圖片中的數字 ---
    text = pytesseract.image_to_string(out, config='digits')
    # --- 識別圖片中的數字母 -----
    # text = pytesseract.image_to_string(out)
    # --- 去掉識別結果中的特殊字符 ---
    exclude_char_list = '.:\\|\'\"?![],()~@#$%^&*_+\|{};<>/$\n-'
    text = ''.join([x for x in text if x not in exclude_char_list])
    print(text)
    return text


def main():
    # --- 識別指定文件目錄下的圖片 ---
    # --- 圖片存放目錄figures ---
    dir = 'C:/Users/user/python/crawler/破解圖形驗證碼/captcha_iSuger/'
    correct_count = 0   # 圖片總數
    total_count = 0     # 識別證確的圖片數量
    # --- 遍歷figures下的png, jpg文件 ---
    for file in os.listdir(dir):
        if file.endswith('.png') or file.endswith('.jpg'):
            # print(file)
            image_path = '%s%s'%(dir, file)     # 圖片路徑
            answer = file.split('.')[0]         # 圖片名稱, 即圖片中的正確文字
            recognition = OCR_lmj(img_path=image_path)    # 圖片識別的文字結果
            # print((answer, recognition))
            print(f'answer: {answer}, recognition: {recognition}')
            if recognition == answer:           # if 識別結果正確, 則total_count +1
                correct_count += 1
            total_count += 1
    print('-'*27)
    print(f'\nTotal count: {total_count}, correct: {correct_count}')

    # --- 單張圖片識別 ---
    '''
    image_path = ''
    OCR_lmj(image_path)
    '''


if __name__ == '__main__':
    main()


