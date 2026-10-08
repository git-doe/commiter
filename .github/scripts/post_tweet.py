import os
import json
import tweepy

def main():
    # Load environment variables
    api_key = os.environ["X_API_KEY"]
    api_secret = os.environ["X_API_SECRET"]
    access_token = os.environ["X_ACCESS_TOKEN"]
    access_secret = os.environ["X_ACCESS_SECRET"]
    
    context = json.loads(os.environ["GITHUB_CONTEXT"])
    event_name = context.get("event_name")
    
    # Authenticate via Tweepy Client (API v2)
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )

    # 1. Prepare Thread Content
    thread_posts = []

    if event_name == "release":
        release = context["event"]["release"]
        tag_name = release.get("tag_name", "New Release")
        body = release.get("body", "No release notes provided.")[:200]
        html_url = release.get("html_url", "")
        
        thread_posts.append(f"🚀 New Release Published: {tag_name}!\n\nRepo: {context['repository']}\nLink: {html_url}")
        thread_posts.append(f"📋 Release Notes:\n\n{body}")
        thread_posts.append(f"Check out the project here: https://github.com/{context['repository']}")

    else:  # 'push' event
        commits = context["event"].get("commits", [])
        if not commits:
            return
        
        latest_commit = commits[-1]
        commit_msg = latest_commit.get("message", "").split("\n")[0][:180]
        commit_url = latest_commit.get("url", "")
        author = latest_commit.get("author", {}).get("name", "Contributor")

        thread_posts.append(f"🔨 New Commit in {context['repository']}\n\n\"{commit_msg}\"\n\nBy {author}")
        thread_posts.append(f"🔗 Commit details: {commit_url}")
        thread_posts.append(f"⭐ Explore the repository: https://github.com/{context['repository']}")

    # 2. Post Thread to Twitter Sequentially
    last_tweet_id = None
    for post in thread_posts[:3]:  # Ensure 1-3 posts max
        if last_tweet_id is None:
            res = client.create_tweet(text=post)
        else:
            res = client.create_tweet(text=post, in_reply_to_tweet_id=last_tweet_id)
        
        last_tweet_id = res.data["id"]
        print(f"Posted Tweet ID: {last_tweet_id}")

if __name__ == "__main__":
    main()
