#!/usr/bin/env python3
"""
Initialize database with sample services
Run this once: python init_db.py
"""

from database import SessionLocal, Service

def init_services():
    db = SessionLocal()
    
    services = [
        # Instagram Services
        {
            'name': 'Instagram Followers',
            'description': 'Real-looking Instagram followers',
            'category': 'Instagram',
            'price_per_1000': 100.0,
            'min_order': 100,
            'max_order': 10000,
            'api_service_id': 'INSTA_FOLLOW_1'
        },
        {
            'name': 'Instagram Likes',
            'description': 'Likes for Instagram posts',
            'category': 'Instagram',
            'price_per_1000': 50.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'INSTA_LIKE_1'
        },
        {
            'name': 'Instagram Views',
            'description': 'Views for Instagram videos/reels',
            'category': 'Instagram',
            'price_per_1000': 30.0,
            'min_order': 100,
            'max_order': 10000,
            'api_service_id': 'INSTA_VIEW_1'
        },
        
        # YouTube Services
        {
            'name': 'YouTube Subscribers',
            'description': 'Subscribers for YouTube channel',
            'category': 'YouTube',
            'price_per_1000': 200.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'YT_SUB_1'
        },
        {
            'name': 'YouTube Views',
            'description': 'Views for YouTube videos',
            'category': 'YouTube',
            'price_per_1000': 40.0,
            'min_order': 100,
            'max_order': 50000,
            'api_service_id': 'YT_VIEW_1'
        },
        {
            'name': 'YouTube Likes',
            'description': 'Likes for YouTube videos',
            'category': 'YouTube',
            'price_per_1000': 60.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'YT_LIKE_1'
        },
        
        # TikTok Services
        {
            'name': 'TikTok Followers',
            'description': 'Followers for TikTok profile',
            'category': 'TikTok',
            'price_per_1000': 150.0,
            'min_order': 100,
            'max_order': 10000,
            'api_service_id': 'TT_FOLLOW_1'
        },
        {
            'name': 'TikTok Likes',
            'description': 'Likes for TikTok videos',
            'category': 'TikTok',
            'price_per_1000': 80.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'TT_LIKE_1'
        },
        {
            'name': 'TikTok Views',
            'description': 'Views for TikTok videos',
            'category': 'TikTok',
            'price_per_1000': 25.0,
            'min_order': 100,
            'max_order': 50000,
            'api_service_id': 'TT_VIEW_1'
        },
        
        # Facebook Services
        {
            'name': 'Facebook Followers',
            'description': 'Followers for Facebook page',
            'category': 'Facebook',
            'price_per_1000': 120.0,
            'min_order': 100,
            'max_order': 10000,
            'api_service_id': 'FB_FOLLOW_1'
        },
        {
            'name': 'Facebook Post Likes',
            'description': 'Likes for Facebook posts',
            'category': 'Facebook',
            'price_per_1000': 70.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'FB_LIKE_1'
        },
        
        # Twitter Services
        {
            'name': 'Twitter Followers',
            'description': 'Followers for Twitter profile',
            'category': 'Twitter',
            'price_per_1000': 130.0,
            'min_order': 100,
            'max_order': 10000,
            'api_service_id': 'TW_FOLLOW_1'
        },
        {
            'name': 'Twitter Retweets',
            'description': 'Retweets for tweets',
            'category': 'Twitter',
            'price_per_1000': 90.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'TW_RT_1'
        },
        {
            'name': 'Twitter Likes',
            'description': 'Likes for tweets',
            'category': 'Twitter',
            'price_per_1000': 60.0,
            'min_order': 50,
            'max_order': 5000,
            'api_service_id': 'TW_LIKE_1'
        }
    ]
    
    for service_data in services:
        service = Service(**service_data)
        db.add(service)
    
    db.commit()
    print(f"✅ Added {len(services)} services to database!")
    db.close()

if __name__ == '__main__':
    init_services()
