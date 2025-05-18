# File: ahp_core.py
# Chứa logic tính toán AHP thuần túy, không phụ thuộc CSDL hay UI

import numpy as np

# Thang đo Saaty
SAATY_SCALE = {
    1: "Quan trọng như nhau",
    3: "Quan trọng hơn một chút",
    5: "Quan trọng hơn nhiều",
    7: "Rất quan trọng hơn",
    9: "Cực kỳ quan trọng hơn"
}
# Các giá trị hợp lệ trên thang Saaty (có thể thêm 2,4,6,8 nếu muốn xử lý chặt chẽ input)
SAATY_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Chỉ số Ngẫu nhiên (Random Index - RI) cho kiểm tra tính nhất quán
RANDOM_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
}

def create_comparison_matrix(num_elements):
    """Tạo một ma trận so sánh cặp rỗng (tất cả các phần tử là 1)."""
    return np.ones((num_elements, num_elements))

def fill_comparison_matrix_from_list(matrix, upper_triangle_values):
    """
    Điền giá trị vào ma trận so sánh cặp từ một danh sách các giá trị của tam giác trên.
    Ma trận đường chéo chính là 1. Các giá trị tam giác dưới là nghịch đảo.
    upper_triangle_values: danh sách các giá trị a_ij với i < j
    """
    n = matrix.shape[0]
    if len(upper_triangle_values) != n * (n - 1) / 2:
        raise ValueError("Số lượng giá trị nhập vào không đủ cho ma trận tam giác trên.")
    
    idx = 0
    for i in range(n):
        for j in range(i + 1, n): # Chỉ lặp qua tam giác trên (j > i)
            value = float(upper_triangle_values[idx])
            if value <= 0: # Giá trị so sánh phải dương
                raise ValueError("Giá trị so sánh cặp phải là số dương.")
            matrix[i, j] = value
            matrix[j, i] = 1 / value # Giá trị đối xứng là nghịch đảo
            idx += 1
    return matrix

def calculate_priority_vector(matrix):
    """
    Tính vector ưu tiên (trọng số) từ ma trận so sánh cặp.
    Sử dụng phương pháp chuẩn hóa trung bình cộng cột (một phương pháp xấp xỉ phổ biến).
    """
    n = matrix.shape[0]
    # 1. Tính tổng các giá trị trong mỗi cột
    col_sums = np.sum(matrix, axis=0) # axis=0 nghĩa là tính tổng theo cột
    
    # 2. Chuẩn hóa ma trận: chia mỗi phần tử cho tổng cột tương ứng
    normalized_matrix = matrix / col_sums
    
    # 3. Tính vector ưu tiên: trung bình cộng các phần tử trên mỗi hàng của ma trận đã chuẩn hóa
    priority_vector = np.mean(normalized_matrix, axis=1) # axis=1 nghĩa là tính trung bình theo hàng
    
    # Đảm bảo tổng vector ưu tiên bằng 1 (thường đã gần bằng 1 sau các bước trên)
    # priority_vector = priority_vector / np.sum(priority_vector) # Có thể bỏ qua nếu muốn
    return priority_vector

def check_consistency(matrix, priority_vector):
    """
    Kiểm tra tính nhất quán của ma trận so sánh cặp.
    Trả về (lambda_max, CI, CR)
    """
    n = matrix.shape[0]
    if n <= 2: # Với ma trận 1x1 hoặc 2x2, luôn nhất quán
        return float(n), 0.0, 0.0

    # 1. Tính vector tổng trọng số (Weighted Sum Vector - WSV)
    # WSV = Ma trận A * Vector trọng số w
    weighted_sum_vector = np.dot(matrix, priority_vector)
    
    # 2. Tính vector nhất quán (Consistency Vector - CV)
    # CV_i = WSV_i / w_i
    # Cần đảm bảo priority_vector[i] không bằng 0, nhưng với cách tính hiện tại thì thường không xảy ra.
    consistency_vector = weighted_sum_vector / priority_vector
    
    # 3. Tính giá trị riêng lớn nhất (Maximum Eigenvalue - lambda_max)
    # lambda_max xấp xỉ bằng trung bình cộng của các phần tử trong CV
    lambda_max = np.mean(consistency_vector)
    
    # 4. Tính Chỉ số Nhất quán (Consistency Index - CI)
    # CI = (lambda_max - n) / (n - 1)
    ci = (lambda_max - n) / (n - 1)
    
    # 5. Tính Tỷ số Nhất quán (Consistency Ratio - CR)
    # CR = CI / RI (Random Index)
    ri = RANDOM_INDEX.get(n) # Lấy RI từ bảng dựa vào n (cấp của ma trận)
    if ri is None or ri == 0: 
        # Nếu không có RI hoặc RI=0 (ví dụ n quá lớn không có trong bảng, hoặc n=1,2),
        # CR không xác định hoặc coi là rất lớn nếu CI > 0
        cr = float('inf') if ci > 0 else 0.0
    else:
        cr = ci / ri
        
    return lambda_max, ci, cr

def normalize_alternative_scores(raw_scores_matrix, criteria_types):
    """
    Chuẩn hóa điểm gốc của các phương án theo từng tiêu chí.
    raw_scores_matrix: Ma trận (số phương án x số tiêu chí) chứa điểm gốc.
    criteria_types: Danh sách các loại tiêu chí ('benefit' hoặc 'cost') tương ứng với mỗi cột.
    """
    # Chuyển raw_scores_matrix sang kiểu float để tính toán
    scores = np.array(raw_scores_matrix, dtype=float)
    num_alternatives, num_criteria = scores.shape
    normalized_scores = np.zeros_like(scores) # Tạo ma trận 0 cùng kích thước

    if len(criteria_types) != num_criteria:
        raise ValueError("Số lượng loại tiêu chí không khớp với số cột điểm của phương án.")

    for j in range(num_criteria): # Lặp qua từng tiêu chí (từng cột)
        column_data = scores[:, j] # Lấy dữ liệu của cột (tiêu chí) hiện tại
        
        if criteria_types[j].lower() == 'benefit': # Tiêu chí lợi ích (càng lớn càng tốt)
            col_sum = np.sum(column_data)
            if col_sum == 0: # Tránh chia cho 0 nếu tất cả điểm là 0
                # Gán giá trị bằng nhau cho tất cả phương án (ví dụ 1/số lượng PA)
                normalized_scores[:, j] = 0.0 if num_alternatives == 0 else (1.0 / num_alternatives)
            else:
                normalized_scores[:, j] = column_data / col_sum
        elif criteria_types[j].lower() == 'cost': # Tiêu chí chi phí (càng nhỏ càng tốt)
            # Biến đổi điểm chi phí: điểm tốt hơn là nghịch đảo của điểm gốc
            # (Cần xử lý nếu điểm gốc là 0)
            # Nếu column_data[i] == 0, gán một giá trị rất nhỏ (epsilon) để tránh lỗi chia cho 0
            column_transformed = 1.0 / np.where(column_data == 0, 1e-9, column_data) 
            col_sum_transformed = np.sum(column_transformed)
            if col_sum_transformed == 0:
                normalized_scores[:, j] = 0.0 if num_alternatives == 0 else (1.0 / num_alternatives)
            else:
                normalized_scores[:, j] = column_transformed / col_sum_transformed
        else:
            raise ValueError(f"Loại tiêu chí không hợp lệ: '{criteria_types[j]}'. Chỉ chấp nhận 'benefit' hoặc 'cost'.")
            
    return normalized_scores

def calculate_overall_scores(normalized_alternative_scores_matrix, criteria_weights_vector):
    """
    Tính điểm tổng hợp cuối cùng cho mỗi phương án.
    Điểm tổng hợp = Ma trận điểm chuẩn hóa của PA * Vector trọng số của Tiêu chí
    """
    # np.dot thực hiện phép nhân ma trận
    return np.dot(normalized_alternative_scores_matrix, criteria_weights_vector)

# Phần này để test nhanh các hàm trong file này (nếu cần)
if __name__ == "__main__":
    print("--- Testing ahp_core.py ---")
    
    # Test tính trọng số tiêu chí
    print("\n1. Test tính trọng số tiêu chí:")
    # Dữ liệu ví dụ từ screenshot của bạn
    # HS vs ĐG: 3, HS vs TK: 5, HS vs GC: 5
    # ĐG vs TK: 3, ĐG vs GC: 5
    # TK vs GC: 5
    # Theo thứ tự (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
    test_crit_comp_values = [3, 5, 5, 3, 5, 5] 
    num_test_criteria = 4
    
    test_crit_matrix = create_comparison_matrix(num_test_criteria)
    try:
        test_filled_crit_matrix = fill_comparison_matrix_from_list(test_crit_matrix, test_crit_comp_values)
        print("Ma trận so sánh cặp tiêu chí (test):\n", test_filled_crit_matrix)

        test_crit_weights = calculate_priority_vector(test_filled_crit_matrix)
        print("\nVector trọng số Tiêu chí (test):\n", test_crit_weights)
        # Kết quả mong đợi gần giống: [0.4732 0.2608 0.1665 0.0995]

        lambda_m, ci_val, cr_val = check_consistency(test_filled_crit_matrix, test_crit_weights)
        print(f"\nKiểm tra nhất quán (test): Lambda_max={lambda_m:.4f}, CI={ci_val:.4f}, CR={cr_val:.4f}")
        # CR mong đợi gần 0.1051 (hoặc 0.0845 nếu lambda_max từ screenshot là 4.228)

    except ValueError as e:
        print(f"Lỗi trong test tiêu chí: {e}")

    # Test chuẩn hóa điểm phương án
    print("\n2. Test chuẩn hóa điểm phương án:")
    test_raw_scores = np.array([
        [15, 5, 24, 23], # PA2 (HS, ĐG, TK, GC)
        [14, 4, 25, 12], # PA1
        [13, 4, 22, 14]  # PA3
    ])
    # Giả sử tất cả là benefit để khớp screenshot (cần cẩn thận nếu 'Giá cả' thực sự là cost)
    test_crit_types = ['benefit', 'benefit', 'benefit', 'benefit'] 
    # Nếu 'Giá cả' là cost: test_crit_types = ['benefit', 'benefit', 'benefit', 'cost']

    print("Điểm gốc (test):\n", test_raw_scores)
    try:
        test_norm_scores = normalize_alternative_scores(test_raw_scores, test_crit_types)
        print("\nĐiểm chuẩn hóa (test):\n", test_norm_scores)
        # Kết quả chuẩn hóa cột đầu (HS): 15/42=0.3571, 14/42=0.3333, 13/42=0.3095
        # (Lưu ý: Screenshot của bạn có thể đã chuẩn hóa trên bộ 4 phương án)
    except ValueError as e:
        print(f"Lỗi trong test chuẩn hóa điểm PA: {e}")

    # Test tính điểm tổng hợp
    if 'test_crit_weights' in locals() and 'test_norm_scores' in locals(): # Chỉ chạy nếu các bước trước thành công
        print("\n3. Test tính điểm tổng hợp:")
        # Giả sử test_crit_weights là trọng số tiêu chí đã tính
        # test_norm_scores là ma trận điểm chuẩn hóa PA
        try:
            test_overall = calculate_overall_scores(test_norm_scores, test_crit_weights)
            print("Điểm tổng hợp các PA (test):\n", test_overall)
        except Exception as e:
            print(f"Lỗi khi tính điểm tổng hợp (test): {e}")