import os
import time
import datetime
from github import Github, Auth

# Authentication
auth = Auth.Token(os.environ["GITHUB_TOKEN"])
g = Github(auth=auth)

onemonthago = datetime.date.today() - datetime.timedelta(days=12)

# Main cleanup loop
for _ in range(100):
    n_deleted = 0
    
    repo = g.get_repo("jackalcooper/mlir-wheels")
    release = repo.get_latest_release()
    assets = release.get_assets()
    
    # 1. Get the initial total count of assets
    remaining_count = assets.totalCount
    
    # 2. Stop immediately if we are already at or below the limit
    if remaining_count <= 500:
        print(f"Asset count is {remaining_count} (<= 500). Stopping.")
        break

    for ass in assets:
        # 3. Stop processing if we hit the floor during deletion
        if remaining_count <= 500:
            print("Reached 500 asset limit. Stopping deletion.")
            break

        if "llvmorg-15.0.7" in ass.name:
            continue
        
        if ass.created_at.date() < onemonthago:
            print(f"Deleting {ass.name} (Remaining: {remaining_count - 1})")
            assert ass.delete_asset()
            n_deleted += 1
            remaining_count -= 1

    if n_deleted == 0:
        break
    
    # Sleep briefly to avoid rate limits before re-fetching
    time.sleep(5)

if n_deleted > 0 and remaining_count > 500:
    # Optional: Raise exception only if we deleted stuff but still have too many 
    # (and likely exited due to the loop range limit, not the count limit)
    pass
