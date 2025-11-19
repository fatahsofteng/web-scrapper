#!/usr/bin/env python3
"""Generate download statistics"""

import json
from pathlib import Path
from datetime import datetime

def generate_stats():
    """Generate download statistics report"""
    downloads_dir = Path('./downloads')

    if not downloads_dir.exists():
        print("No downloads folder found")
        return

    stats = {
        'timestamp': datetime.now().isoformat(),
        'successful_downloads': 0,
        'failed_downloads': 0,
        'total_size_mb': 0,
        'average_size_mb': 0,
        'videos': []
    }

    successful_videos = []

    for video_dir in downloads_dir.iterdir():
        if not video_dir.is_dir():
            continue

        video_id = video_dir.name
        m4a_files = list(video_dir.glob('*.m4a'))
        json_files = list(video_dir.glob('*.json'))

        if m4a_files and json_files:
            # Successful download
            stats['successful_downloads'] += 1

            m4a_file = m4a_files[0]
            size_mb = m4a_file.stat().st_size / (1024 * 1024)
            stats['total_size_mb'] += size_mb

            # Read metadata
            with open(json_files[0], 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            successful_videos.append({
                'video_id': video_id,
                'size_mb': round(size_mb, 2),
                'duration_sec': metadata.get('duration_sec', 0),
                'title': metadata.get('title', 'Unknown')
            })
        else:
            # Failed download
            stats['failed_downloads'] += 1

    if stats['successful_downloads'] > 0:
        stats['average_size_mb'] = stats['total_size_mb'] / stats['successful_downloads']

    stats['videos'] = successful_videos
    stats['total_size_mb'] = round(stats['total_size_mb'], 2)
    stats['average_size_mb'] = round(stats['average_size_mb'], 2)

    # Print report
    print("=" * 50)
    print("YouTube Download Statistics Report")
    print("=" * 50)
    print(f"Timestamp: {stats['timestamp']}")
    print(f"Successful downloads: {stats['successful_downloads']} ✅")
    print(f"Failed downloads: {stats['failed_downloads']} ❌")
    print(f"Total size: {stats['total_size_mb']} MB")
    print(f"Average size: {stats['average_size_mb']} MB per video")
    print("=" * 50)

    # Save to file
    with open('download_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("\n✓ Stats saved to download_stats.json")

    return stats

if __name__ == '__main__':
    generate_stats()
