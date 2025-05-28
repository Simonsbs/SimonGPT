import os
import time
import asyncio
import asyncpg
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Load environment variables
load_dotenv()
WATCH_DIR = os.getenv("WATCH_DIR", os.path.abspath("./watched"))
DB_URL     = os.getenv("VECTOR_DB_URL")

# Import your ingestion entrypoint
from ingest import main as ingest_file_async


class SimpleIngestHandler(FileSystemEventHandler):
    """Runs ingestion immediately on file events, cleaning up old rows first."""

    def _delete_records(self, path: str):
        """Remove DB entries for a given file path."""
        async def _do_delete():
            conn = await asyncpg.connect(DB_URL)
            await conn.execute(
                "DELETE FROM public.documents WHERE source = $1", path
            )
            await conn.close()
        # Run the async delete synchronously
        asyncio.run(_do_delete())

    def on_created(self, event):
        if not event.is_directory:
            print(f"[watcher] File created:  {event.src_path}")
            self._delete_records(event.src_path)
            asyncio.run(ingest_file_async(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[watcher] File modified: {event.src_path}")
            self._delete_records(event.src_path)
            asyncio.run(ingest_file_async(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[watcher] File deleted:  {event.src_path}")
            self._delete_records(event.src_path)


def main():
    # 1) Ensure watch directory exists
    os.makedirs(WATCH_DIR, exist_ok=True)

    # 2) Initial ingest of existing files
    handler = SimpleIngestHandler()
    for fname in os.listdir(WATCH_DIR):
        full_path = os.path.join(WATCH_DIR, fname)
        if os.path.isfile(full_path):
            print(f"[watcher] Initial ingest: {full_path}")
            handler._delete_records(full_path)
            asyncio.run(ingest_file_async(full_path))

    # 3) Start observer
    observer = Observer()
    observer.schedule(handler, WATCH_DIR, recursive=False)
    observer.start()
    print(f"[watcher] Now monitoring '{WATCH_DIR}' for changes. Press Ctrl+C to exit.")

    # 4) Keep running until Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watcher] Shutdown requested, stopping…")
        observer.stop()
    observer.join()
    print("[watcher] Stopped.")

if __name__ == "__main__":
    main()
