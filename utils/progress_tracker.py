
import time

class ProgressTracker:
    def __init__(self, total_items, update_interval=1000):
        self.total_items = total_items
        self.current_count = 0
        self.start_time = time.time()
        self.update_interval = update_interval

    def update(self, count=1):
       #Actualiza el progreso y muestra el estado si se alcanza el intervalo
        self.current_count += count
        if self.current_count % self.update_interval == 0:
            self._show_progress()

    def _show_progress(self):
        #Mostrar información de progreso
        elapsed_time = time.time() - self.start_time
        progress = (self.current_count / self.total_items) * 100
        items_per_second = self.current_count / elapsed_time if elapsed_time > 0 else 0
        
        print(f"Progress: {progress:.1f}% ({self.current_count}/{self.total_items})")
        print(f"Processing speed: {items_per_second:.1f} items/second")
        print(f"Elapsed time: {elapsed_time:.1f} seconds")