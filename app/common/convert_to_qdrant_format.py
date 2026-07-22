from typing import List
import numpy as np

def convert_single_to_qdrant(result: np.ndarray) -> List[float]:
    """
    将单个 feature_extraction() 的返回值转换为 Qdrant 兼容的 list[float]
    """
    if result.ndim == 2:
        result = result[0]

    return result.tolist()


def convert_batch_to_qdrant(result: np.ndarray) -> List[List[float]]:
    """
    将批量 feature_extraction() 的返回值转换为 Qdrant 兼容的 List[List[float]]
    """
    return result.tolist()


# ============ 使用示例 ============
if __name__ == "__main__":

    # 单条文本 Embedding（模拟 feature_extraction 返回值）
    single_embedding = np.array([[0.12, 0.34, 0.56, 0.78]])
    single_vector = convert_single_to_qdrant(single_embedding)
    print("单条向量：")
    print(single_vector)
    print("single_vector_type:", type(single_vector))
    # 输出：[0.12, 0.34, 0.56, 0.78]

    # 批量文本 Embedding（模拟 feature_extraction 返回值）
    batch_embedding = np.array([
        [0.11, 0.22, 0.33],
        [0.44, 0.55, 0.66],
        [0.77, 0.88, 0.99],
    ])
    batch_vectors = convert_batch_to_qdrant(batch_embedding)
    print("\n批量向量：")
    print(batch_vectors)
    print("batch_vectors_type:", type(batch_vectors))
    # 输出：
    # [
    #   [0.11, 0.22, 0.33],
    #   [0.44, 0.55, 0.66],
    #   [0.77, 0.88, 0.99]
    # ]