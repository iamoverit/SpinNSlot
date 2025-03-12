from django.core.cache.backends.filebased import FileBasedCache

class CustomFileBasedCache(FileBasedCache):
    def incr(self, key, delta=1, version=None):
        """Имитация `incr()`, необходимая для работы django-ratelimit"""
        value = self.get(key, version=version)
        if value is None:
            raise ValueError(f"Key '{key}' not found in cache")
        new_value = int(value) + delta
        self.set(key, new_value, version=version)
        return new_value

    def decr(self, key, delta=1, version=None):
        """Имитация `decr()` аналогично `incr()`"""
        return self.incr(key, -delta, version)

