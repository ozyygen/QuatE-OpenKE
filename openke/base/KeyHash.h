#include "HashNode.h"
#include "HashMap.h"

// Default hash function class
template <typename K, size_t tableSize>
struct KeyHash {
    unsigned long operator()(const K &key) const
    {
        return reinterpret_cast<unsigned long>(key) % tableSize;
    }
};