import random
from models import AllocationHistory, db

BLOCK_SIZE = 4096  # 4KB
STORAGE_SIZE = 100 * 1024 * 1024 // BLOCK_SIZE  # Simulando armazenamento com 100MB em blocos de 4KB

class ContiguousAllocation:
    def __init__(self):
        self.storage = [None] * STORAGE_SIZE

    def first_fit(self, file_id, size):
        for i in range(len(self.storage) - size + 1):
            if all(block is None for block in self.storage[i:i + size]):
                for j in range(size):
                    self.storage[i + j] = file_id
                return f"Contiguous (FirstFit) allocation from block {i} to block {i + size - 1}"
        return "Failed to allocate contiguously (FirstFit)"

    def best_fit(self, file_id, size):
        best_index = -1
        best_size = float('inf')
        for i in range(len(self.storage) - size + 1):
            if all(block is None for block in self.storage[i:i + size]):
                free_size = sum(1 for block in self.storage[i:] if block is None)
                if free_size < best_size:
                    best_size = free_size
                    best_index = i
        if best_index != -1:
            for j in range(size):
                self.storage[best_index + j] = file_id
            return f"Contiguous (BestFit) allocation from block {best_index} to block {best_index + size - 1}"
        return "Failed to allocate contiguously (BestFit)"

    def worst_fit(self, file_id, size):
        worst_index = -1
        worst_size = 0
        for i in range(len(self.storage) - size + 1):
            if all(block is None for block in self.storage[i:i + size]):
                free_size = sum(1 for block in self.storage[i:] if block is None)
                if free_size > worst_size:
                    worst_size = free_size
                    worst_index = i
        if worst_index != -1:
            for j in range(size):
                self.storage[worst_index + j] = file_id
            return f"Contiguous (WorstFit) allocation from block {worst_index} to block {worst_index + size - 1}"
        return "Failed to allocate contiguously (WorstFit)"

class LinkedAllocation:
    def __init__(self):
        self.storage = [None] * STORAGE_SIZE

    def allocate(self, file_id, size):
        free_blocks = [i for i, block in enumerate(self.storage) if block is None]
        if len(free_blocks) < size:
            return "Failed to allocate using linked allocation"

        for i in range(size):
            self.storage[free_blocks[i]] = (file_id, free_blocks[i + 1] if i + 1 < size else -1)
        return f"Linked allocation using blocks {free_blocks}"

class IndexedAllocation:
    def __init__(self):
        self.storage = [None] * STORAGE_SIZE
        self.index_table = {}

    def allocate(self, file_id, size):
        free_blocks = [i for i, block in enumerate(self.storage) if block is None]
        if len(free_blocks) < size + 1:  # +1 para o bloco de índice
            return "Failed to allocate using indexed allocation"

        index_block = free_blocks[0]
        self.index_table[file_id] = index_block
        self.storage[index_block] = free_blocks[1:size + 1]
        for block in free_blocks[1:size + 1]:
            self.storage[block] = file_id
        return f"Indexed allocation with index block {index_block} and data blocks {free_blocks[1:size + 1]}"

contiguous_allocation = ContiguousAllocation()
linked_allocation = LinkedAllocation()
indexed_allocation = IndexedAllocation()

def allocate_file(file_id, size):
    size_in_blocks = (size + BLOCK_SIZE - 1) // BLOCK_SIZE  # Convertendo o tamanho para blocos
    if size_in_blocks <= 5:
        allocation_method = "FirstFit"
        result = contiguous_allocation.first_fit(file_id, size_in_blocks)
    elif size_in_blocks <= 15:
        allocation_method = "BestFit"
        result = contiguous_allocation.best_fit(file_id, size_in_blocks)
    elif size_in_blocks <= 25:
        allocation_method = "WorstFit"
        result = contiguous_allocation.worst_fit(file_id, size_in_blocks)
    elif size_in_blocks <= 40:
        allocation_method = "Linked"
        result = linked_allocation.allocate(file_id, size_in_blocks)
    else:
        allocation_method = "Indexed"
        result = indexed_allocation.allocate(file_id, size_in_blocks)

    # Salvar o histórico de alocação
    allocation_history = AllocationHistory(file_id=file_id, allocation_method=allocation_method)
    db.session.add(allocation_history)
    db.session.commit()

    return result
