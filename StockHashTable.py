class HashObject:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None
        self.prev = None

class StockHashTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size
        pass
    
    def add(self, key, value):
        index = hash(key) % self.size
        if self.table[index] is None:         #No collision
            self.table[index] = HashObject(key, value)
        else:                               #Handle collision
            head = self.table[index]
            while head.next is not None:
                head = head.next
            head.next = HashObject(key, value)

    def delete(self, key):
        index = hash(key) % self.size
        if self.table[index] is None:
            return False
        else:
            head = self.table[index]
            if head.key == key:
                self.table[index] = head.next
                return True
            else:
                while head.next is not None:
                    if head.next.key == key:
                        head.next = head.next.next
                        return True
                    head = head.next
                return False
            

    def get(self, key):
        index = hash(key) % self.size
        if self.table[index] is None:
            return None
        else:
            head = self.table[index]
            while head is not None:
                if head.key == key:
                    return head.value
                head = head.next
            return None