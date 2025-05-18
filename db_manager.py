# File: db_manager.py
import pymysql
from pymysql import Error
import numpy as np
import json # Để chuyển đổi ma trận sang JSON string

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'ahp_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_connection():
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
    except Error as e:
        print(f"Lỗi kết nối CSDL (PyMySQL): {e}")
    return conn

# === Decisions ===
def add_decision(name, description="", criteria_cr_value=None, criteria_comparison_matrix_json=None):
    conn = create_connection()
    decision_id = None
    if conn:
        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO decisions 
                    (decision_name, description, criteria_cr, criteria_comparison_json) 
                    VALUES (%s, %s, %s, %s)
                """
                params = (name, description, criteria_cr_value, criteria_comparison_matrix_json)
                cursor.execute(query, params)
                conn.commit()
                decision_id = cursor.lastrowid
        except Error as e:
            print(f"Lỗi khi thêm quyết định: {e}. Params: {params}") # In params để debug
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return decision_id

def get_all_decisions():
    conn = create_connection()
    decisions = []
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM decisions ORDER BY creation_date DESC"
                cursor.execute(query)
                decisions = cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy danh sách quyết định: {e}")
        finally:
            if conn: conn.close()
    return decisions

def get_decision_by_id(decision_id):
    conn = create_connection()
    decision = None
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM decisions WHERE decision_id = %s"
                cursor.execute(query, (decision_id,))
                decision = cursor.fetchone()
        except Error as e:
            print(f"Lỗi khi lấy quyết định ID {decision_id}: {e}")
        finally:
            if conn: conn.close()
    return decision

def delete_decision_by_id(decision_id):
    conn = create_connection()
    success = False
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "DELETE FROM decisions WHERE decision_id = %s"
                cursor.execute(query, (decision_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    success = True
        except Error as e:
            print(f"Lỗi khi xóa quyết định ID {decision_id}: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return success

# === Criteria ===
def add_criterion(decision_id, criterion_name, weight=None):
    conn = create_connection()
    criterion_id = None
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "INSERT INTO criteria (decision_id, criterion_name, weight) VALUES (%s, %s, %s)"
                # Đảm bảo weight là float hoặc None
                weight_to_save = float(weight) if weight is not None else None
                cursor.execute(query, (decision_id, criterion_name, weight_to_save))
                conn.commit()
                criterion_id = cursor.lastrowid
        except Error as e:
            print(f"Lỗi khi thêm tiêu chí: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return criterion_id

def get_criteria_for_decision(decision_id):
    conn = create_connection()
    criteria_list = []
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM criteria WHERE decision_id = %s ORDER BY criterion_id ASC"
                cursor.execute(query, (decision_id,))
                criteria_list = cursor.fetchall()
        except Error as e:
            print(f"Lỗi khi lấy tiêu chí cho quyết định {decision_id}: {e}")
        finally:
            if conn: conn.close()
    return criteria_list

# === Criteria Comparison (Không dùng trực tiếp trong app.py của bản này, nhưng để lại nếu muốn phát triển) ===
def save_criteria_comparison_matrix_to_separate_table(decision_id, criteria_ids_in_order, matrix_values):
    # Hàm này sẽ lưu vào bảng `criteria_comparison`
    conn = create_connection()
    success = False
    if conn:
        try:
            with conn.cursor() as cursor:
                del_query = "DELETE FROM criteria_comparison WHERE decision_id = %s"
                cursor.execute(del_query, (decision_id,))
                
                insert_query = "INSERT INTO criteria_comparison (decision_id, criterion1_id, criterion2_id, value) VALUES (%s, %s, %s, %s)"
                num_criteria = len(criteria_ids_in_order)
                for i in range(num_criteria):
                    for j in range(i + 1, num_criteria):
                        crit1_id = criteria_ids_in_order[i]
                        crit2_id = criteria_ids_in_order[j]
                        value_to_save = float(matrix_values[i, j])
                        cursor.execute(insert_query, (decision_id, crit1_id, crit2_id, value_to_save))
                conn.commit()
                success = True
        except Error as e:
            print(f"Lỗi khi lưu ma trận so sánh tiêu chí (bảng riêng): {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return success

def get_criteria_comparison_matrix_from_separate_table(decision_id, num_criteria, criteria_id_to_index_map):
    # Hàm này sẽ đọc từ bảng `criteria_comparison`
    conn = create_connection()
    matrix = np.ones((num_criteria, num_criteria), dtype=float)
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "SELECT criterion1_id, criterion2_id, value FROM criteria_comparison WHERE decision_id = %s"
                cursor.execute(query, (decision_id,))
                rows = cursor.fetchall()
                for row in rows:
                    idx1 = criteria_id_to_index_map.get(row['criterion1_id'])
                    idx2 = criteria_id_to_index_map.get(row['criterion2_id'])
                    if idx1 is not None and idx2 is not None:
                        value_from_db = float(row['value'])
                        matrix[idx1, idx2] = value_from_db
                        matrix[idx2, idx1] = 1.0 / value_from_db if value_from_db != 0 else float('inf')
        except Error as e:
            print(f"Lỗi khi lấy ma trận so sánh tiêu chí (bảng riêng): {e}")
        finally:
            if conn: conn.close()
    return matrix

# === Alternatives & Scores ===
def add_alternative(decision_id, alternative_name):
    conn = create_connection()
    alt_id = None
    if conn:
        try:
            with conn.cursor() as cursor:
                query = "INSERT INTO alternatives (decision_id, alternative_name) VALUES (%s, %s)"
                cursor.execute(query, (decision_id, alternative_name))
                conn.commit()
                alt_id = cursor.lastrowid
        except Error as e:
            print(f"Lỗi khi thêm phương án: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return alt_id

def save_alternative_raw_score(alternative_id, criterion_id, raw_score):
    conn = create_connection()
    success = False
    if conn:
        try:
            with conn.cursor() as cursor:
                check_query = "SELECT score_id FROM alternative_scores WHERE alternative_id = %s AND criterion_id = %s"
                cursor.execute(check_query, (alternative_id, criterion_id))
                existing_score = cursor.fetchone()

                if existing_score:
                    query = "UPDATE alternative_scores SET raw_score = %s WHERE score_id = %s"
                    params = (float(raw_score), existing_score['score_id'])
                else:
                    query = "INSERT INTO alternative_scores (alternative_id, criterion_id, raw_score) VALUES (%s, %s, %s)"
                    params = (alternative_id, criterion_id, float(raw_score))
                cursor.execute(query, params)
                conn.commit()
                success = True
        except Error as e:
            print(f"Lỗi khi lưu điểm gốc phương án: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return success

def update_alternative_details(alternative_id, normalized_scores_dict, overall_score, rank_value):
    conn = create_connection()
    success = False
    if conn:
        try:
            with conn.cursor() as cursor:
                alt_update_query = "UPDATE alternatives SET overall_score = %s, rank_value = %s WHERE alternative_id = %s"
                cursor.execute(alt_update_query, (float(overall_score), int(rank_value), alternative_id))

                # Đảm bảo các dòng trong alternative_scores đã được tạo khi lưu raw_score
                # Nếu chưa, bạn cần INSERT trước khi UPDATE normalized_score
                score_update_query = """
                    UPDATE alternative_scores SET normalized_score = %s 
                    WHERE alternative_id = %s AND criterion_id = %s
                """
                for crit_id, norm_score in normalized_scores_dict.items():
                    # Kiểm tra xem dòng có tồn tại không, nếu không thì có thể INSERT mới với raw_score = NULL
                    # Hoặc giả định nó đã được tạo bởi save_alternative_raw_score
                    cursor.execute(score_update_query, (float(norm_score), alternative_id, crit_id))
                conn.commit()
                success = True
        except Error as e:
            print(f"Lỗi khi cập nhật chi tiết phương án: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
    return success

def get_alternatives_with_scores_for_decision(decision_id):
    conn = create_connection()
    alternatives_data = []
    if conn:
        try:
            with conn.cursor() as cursor:
                alt_query = """
                    SELECT alt.alternative_id, alt.alternative_name, alt.overall_score, alt.rank_value
                    FROM alternatives alt
                    WHERE alt.decision_id = %s
                    ORDER BY alt.rank_value ASC, alt.overall_score DESC 
                """
                cursor.execute(alt_query, (decision_id,))
                alts_basic_info = cursor.fetchall()

            # Tạo connection mới hoặc đảm bảo connection cũ vẫn mở cho các query phụ
            # Trong trường hợp này, vì `with conn.cursor()` đã đóng cursor, 
            # ta cần đảm bảo `conn` vẫn mở hoặc tạo lại `conn` và `cursor` mới.
            # Cách đơn giản là fetch hết rồi mới xử lý tiếp.
            
            # Để tránh lỗi cursor đã đóng, ta sẽ thực hiện query phụ trong một context connection mới nếu cần
            # Hoặc tốt hơn là giữ connection mở cho đến khi tất cả các query hoàn tất.
            # Phiên bản trước dùng `with conn.cursor() as score_cursor:` cho query phụ là ổn.
            
            # Với cấu trúc hiện tại (mỗi hàm tự quản lý connection), ta có thể làm như sau:
            conn_for_scores = create_connection() # Mở connection mới cho các query phụ
            if conn_for_scores:
                try:
                    for alt_info in alts_basic_info:
                        current_alt_id = alt_info['alternative_id']
                        with conn_for_scores.cursor() as score_cursor:
                            scores_query = """
                                SELECT sc.criterion_id, c.criterion_name, sc.raw_score, sc.normalized_score
                                FROM alternative_scores sc
                                JOIN criteria c ON sc.criterion_id = c.criterion_id
                                WHERE sc.alternative_id = %s
                                ORDER BY c.criterion_id ASC
                            """
                            score_cursor.execute(scores_query, (current_alt_id,))
                            scores_details_list = score_cursor.fetchall()
                        alt_info['scores_detail'] = scores_details_list
                        alternatives_data.append(alt_info)
                finally:
                    conn_for_scores.close()
            else: # Nếu không mở được connection phụ
                 alternatives_data = alts_basic_info # Trả về thông tin cơ bản nếu không lấy được điểm chi tiết

        except Error as e:
            print(f"Lỗi khi lấy phương án và điểm (QĐ ID: {decision_id}, PyMySQL): {e}")
        finally:
            if conn and conn.open: conn.close() # Đóng connection chính nếu nó còn mở
    return alternatives_data


if __name__ == "__main__":
    print("--- Testing db_manager.py (PyMySQL) ---")
    test_conn = create_connection()
    if test_conn:
        print("1. Kết nối CSDL thành công!")
        print("\n2. Danh sách quyết định:")
        all_decs = get_all_decisions()
        if all_decs:
            for dec in all_decs:
                print(f"   - ID: {dec['decision_id']}, Tên: {dec['decision_name']}, CR: {dec.get('criteria_cr', 'N/A')}, Ma trận JSON: {dec.get('criteria_comparison_json', 'N/A') != None}")
        else:
            print("   Không có quyết định nào.")
        test_conn.close()
    else:
        print("1. Kết nối CSDL thất bại.")