#!/usr/bin/env python3
"""Clean up failed downloads"""

import os
import shutil
from pathlib import Path

def cleanup_failed_downloads():
    """Remove incomplete downloads (.part files and folders without .m4a)"""
    downloads_dir = Path('./downloads')

    if not downloads_dir.exists():
        print("No downloads folder found")
        return

    removed_count = 0

    for video_dir in downloads_dir.iterdir():
        if not video_dir.is_dir():
            continue

        # Check if has .m4a file (successful)
        has_m4a = any(video_dir.glob('*.m4a'))

        # If no .m4a, it's a failed download
        if not has_m4a:
            print(f"Removing failed: {video_dir.name}")
            shutil.rmtree(video_dir)
            removed_count += 1

    print(f"\n✓ Removed {removed_count} failed downloads")

    # Count successful
    successful = sum(1 for d in downloads_dir.iterdir() if d.is_dir())
    print(f"✓ Remaining successful: {successful} videos")

if __name__ == '__main__':
    cleanup_failed_downloads()
